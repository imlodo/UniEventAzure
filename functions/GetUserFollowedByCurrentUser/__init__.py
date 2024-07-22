import logging
import os
import json
import random

import jwt
from bson import ObjectId
from pymongo import MongoClient
import azure.functions as func

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
users_collection = db.Users
follow_user_collection = db.FollowUser


def get_followed_users(t_username, limit=None):
    followed_aliases = follow_user_collection.find({"t_alias_generated_from": t_username},
                                                   {"t_alias_generated_to": 1, "_id": 0})
    followed_aliases = [follow['t_alias_generated_to'] for follow in followed_aliases]

    query = {"t_alias_generated": {"$in": followed_aliases}}
    users = users_collection.find(query)

    user_list = []
    for user in users:
        t_follower_number = follow_user_collection.count_documents(
            {"t_alias_generated_to": user.get("t_alias_generated", "null")})
        user_dict = {
            "_id": str(user["_id"]),
            "t_username": user.get("t_username", ""),
            "t_name": user.get("t_name", ""),
            "t_surname": user.get("t_surname", ""),
            "t_alias_generated": user.get("t_alias_generated", ""),
            "t_description": user.get("t_description", ""),
            "t_profile_photo": user.get("t_profile_photo", ""),
            "is_verified": user.get("is_verified", False),
            "t_type": user.get("t_type", ""),
            "t_role": user.get("t_role", ""),
            "t_follower_number": t_follower_number
        }
        user_list.append(user_dict)

    if limit:
        user_list = user_list[:limit]

    return user_list


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            alias_generated = req.params.get("t_alias_generated")
            if alias_generated:
                print(alias_generated)
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    status_code=404
                )

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')

            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    status_code=404
                )
            except jwt.InvalidTokenError:
                return func.HttpResponse(
                    status_code=404
                )

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    status_code=404
                )

            limit = req.params.get('limit')
            if limit:
                limit = int(limit)

            followed_users = get_followed_users(t_username, limit)

            if limit:
                followed_users = followed_users[:limit]

            return func.HttpResponse(
                json.dumps({"followed_users": followed_users}, default=str),
                status_code=200,
                mimetype='application/json'
            )
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero degli utenti seguiti.",
                status_code=500
            )
    else:
        return func.HttpResponse(
            status_code=404
        )
