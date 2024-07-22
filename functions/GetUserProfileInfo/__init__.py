import logging
import os
import pymongo
import jwt
from datetime import datetime
from azure.functions import HttpResponse
from pymongo import MongoClient
import azure.functions as func
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
users_collection = db.Users
content_collection = db.Contents
content_booked_collection = db.ContentBooked
content_liked_collection = db.ContentLiked
follow_user_collection = db.FollowUser

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Funzione per ottenere i dettagli dell'utente
def get_user_info(t_alias_generated):
    user = users_collection.find_one({"t_alias_generated": t_alias_generated})
    if user:
        if '_id' in user:
            del user['_id']
        if 't_password' in user:
            del user['t_password']
        return user
    return None


# Funzione per ottenere i contenuti dell'utente (ultimi 5)
def get_user_content(t_alias_generated, limit=5):
    contents = content_collection.find({"t_alias_generated": t_alias_generated}).sort("created_date",
                                                                                      pymongo.DESCENDING).limit(limit)
    content_list = []
    for content in contents:
        if '_id' in content:
            del content['_id']
        content_list.append(content)
    return content_list


# Funzione per ottenere i contenuti aggiunti ai preferiti dall'utente (ultimi 5)
def get_user_booked_content(t_username, limit=5):
    booked_contents = content_booked_collection.find({"t_username": t_username}).sort(
        "created_date", pymongo.DESCENDING).limit(limit)
    content_list = []
    for booked in booked_contents:
        content = content_collection.find_one({"_id": booked["content_id"]})
        if content:
            if '_id' in content:
                del content['_id']
            content_list.append(content)
    return content_list


# Funzione per ottenere i contenuti piaciuti dall'utente (ultimi 5)
def get_user_liked_content(t_alias_generated, limit=5):
    liked_contents = content_liked_collection.find({"t_user.t_alias_generated": t_alias_generated}).sort("created_date",
                                                                                                         pymongo.DESCENDING).limit(
        limit)
    content_list = []
    for liked in liked_contents:
        content = content_collection.find_one({"_id": liked["content_id"]})
        if content:
            if '_id' in content:
                del content['_id']
            content_list.append(content)
    return content_list


# Funzione per ottenere il conteggio dei likes
def get_count_like(t_alias_generated):
    liked_contents = content_liked_collection.find({"t_user.t_alias_generated": t_alias_generated})
    return liked_contents.count()


# Funzione per ottenere il conteggio dei follower
def get_count_follower(t_alias_generated):
    followers = follow_user_collection.find({"t_username_1": t_alias_generated})
    return followers.count()


# Funzione per ottenere il conteggio delle persone seguite
def get_count_followed(t_alias_generated):
    followed = follow_user_collection.find({"t_username_2": t_alias_generated})
    return followed.count()


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return HttpResponse(status_code=404)

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')
            try:
                jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return HttpResponse(status_code=404)
            except jwt.InvalidTokenError:
                return HttpResponse(status_code=404)

            # Ottieni l'alias dall'URL della richiesta
            t_alias_generated = req.params.get('t_alias_generated')
            user = users_collection.find_one({"t_alias_generated": t_alias_generated})
            if not user:
                return HttpResponse(
                    "User non trovato",
                    status_code=404
                )
            if not t_alias_generated:
                return HttpResponse(
                    "Parametro t_alias_generated mancante.",
                    status_code=400
                )

            # Ottieni le informazioni dell'utente dal database
            user_info = get_user_info(t_alias_generated)
            if not user_info:
                return HttpResponse(status_code=404)

            # Ottieni i contenuti dell'utente dal database (ultimi 5)
            content_list = get_user_content(t_alias_generated)
            booked_list = get_user_booked_content(user.get("t_username"))
            liked_list = get_user_liked_content(t_alias_generated)

            # Ottieni i conteggi
            count_followed = get_count_followed(t_alias_generated)
            count_follower = get_count_follower(t_alias_generated)
            count_like = get_count_like(t_alias_generated)

            # Costruisci l'oggetto UserProfileInfo
            user_profile_info = {
                "contentList": content_list,
                "bookedList": booked_list,
                "likedList": liked_list,
                "countFollowed": count_followed,
                "countFollower": count_follower,
                "countLike": count_like,
                "isPublic": user_info.get("is_public", True)
            }

            # Costruisci il corpo della risposta come oggetto JSON
            response_body = json.dumps({"user_profile_info": user_profile_info})

            return HttpResponse(
                body=response_body,
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return HttpResponse(
                "Si è verificato un errore durante il recupero delle informazioni utente.",
                status_code=500
            )

    else:
        return HttpResponse(
            status_code=404
        )
