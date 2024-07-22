import logging
import os
import random

import pymongo
import jwt
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
content_collection = db.Contents
maps_collection = db.EventMaps
location_collection = db.EventLocation
reviews_collection = db.TicketReviews

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def search_event_by_caption_liked(event_caption_liked):
    events = content_collection.find({"t_caption": {"$regex": event_caption_liked, "$options": "i"}}).limit(10)
    events_list = []
    for event in events:
        event_id = event.get("id")

        # Recupera le mappe legate all'evento
        maps = list(maps_collection.find({"t_map_event_id": event_id}))

        # Recupera la location legata all'evento
        location = location_collection.find_one({"event_id": event_id})

        # Recupera le recensioni legate all'evento
        reviews = list(reviews_collection.find({"t_event_id": event_id}))

        # Rimuovi l'ID se presente (per esempio, se è un ObjectId)
        event.pop('_id', None)

        # Aggiungi mappe, location e recensioni all'evento
        event["t_map_list"] = maps if maps else None
        event["t_location"] = location if location else None
        event["t_reviews"] = reviews if reviews else None

        events_list.append(event)

    return events_list


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Controlla che il metodo della richiesta sia GET
    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            t_caption_liked = req.params.get("t_caption_liked")
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

            # Cerca gli eventi corrispondenti al parametro t_caption_liked
            if t_caption_liked:
                event_list = search_event_by_caption_liked(t_caption_liked)
            else:
                return func.HttpResponse(
                    status_code=404
                )

            if event_list:
                # Costruisci il corpo della risposta come oggetto JSON
                response_body = json.dumps({"events": event_list})

                return func.HttpResponse(
                    body=response_body,
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    status_code=404
                )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero delle informazioni utente.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            status_code=404
        )
