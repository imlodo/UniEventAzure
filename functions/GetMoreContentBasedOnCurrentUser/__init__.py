import logging
import os
import random
from collections import Counter
from datetime import datetime, timedelta

import pymongo
from azure.functions import HttpResponse
from pymongo import MongoClient
import azure.functions as func
import json
import jwt

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
content_collection = db.Contents
users_collection = db.Users
content_like_collection = db.ContentLike
content_booked_collection = db.ContentBooked
content_discussion_collection = db.ContentDiscussion

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def calculate_user_preferences(t_username):
    user_preferences = Counter()

    # Conteggia i like dell'utente
    likes = content_like_collection.find({"t_username": t_username})
    for like in likes:
        content = content_collection.find_one({"_id": like["content_id"]})
        if content:
            user_preferences.update(content.get("hashtags", []))

    # Conteggia i contenuti preferiti dall'utente
    bookings = content_booked_collection.find({"t_username": t_username})
    for booking in bookings:
        content = content_collection.find_one({"_id": booking["content_id"]})
        if content:
            user_preferences.update(content.get("hashtags", []))

    # Conteggia i commenti dell'utente
    discussions = content_discussion_collection.find({"t_username": t_username})
    for discussion in discussions:
        content = content_collection.find_one({"_id": discussion["content_id"]})
        if content:
            user_preferences.update(content.get("hashtags", []))

    return user_preferences


def get_recommended_content(user_preferences, order_by, order_direction, pageNumber, pageSize):
    query = {"hashtags": {"$in": list(user_preferences.keys())}}
    sort_order = pymongo.ASCENDING if order_direction == "ASC" else pymongo.DESCENDING

    contents = content_collection.find(query).sort(order_by, sort_order).skip((pageNumber - 1) * pageSize).limit(
        pageSize)

    content_list = []
    for content in contents:
        content["preference_score"] = sum(user_preferences.get(tag, 0) for tag in content.get("hashtags", []))
        if '_id' in content:
            del content['_id']
        content_list.append(content)

    content_list.sort(key=lambda x: x["preference_score"], reverse=True)

    return content_list

def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        try:
            token = req.headers.get('Authorization')
            if not token:
                return HttpResponse("Token mancante.", status_code=401)

            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    "Autorizzazione non valida.",
                    status_code=401
                )

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')

            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    "Token scaduto.",
                    status_code=401
                )
            except jwt.InvalidTokenError:
                return func.HttpResponse(
                    "Token non valido.",
                    status_code=401
                )

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    "Token non contiene un username valido.",
                    status_code=401
                )

            req_body = req.get_json()
            order_by = req_body.get('order_by', 'created_date')
            order_direction = req_body.get('order_direction', 'DESC')
            pageNumber = req_body.get('pageNumber', 1)
            pageSize = req_body.get('pageSize', 10)

            user_preferences = calculate_user_preferences(t_username)
            content_list = get_recommended_content(user_preferences, order_by, order_direction, pageNumber, pageSize)

            response_body = json.dumps({"content_list": content_list})

            return HttpResponse(
                body=response_body,
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return HttpResponse(
                "Si è verificato un errore durante il recupero dei contenuti.",
                status_code=500
            )

    else:
        return HttpResponse(
            status_code=404
        )
