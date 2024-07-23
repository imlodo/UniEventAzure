import logging
import os
import random
from datetime import datetime
import pymongo
from bson import ObjectId
from pymongo import MongoClient
import azure.functions as func
import jwt
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni (crea le collezioni se non esistono)
content_collection = db.Contents
content_tags_collections = db.ContentTags
content_mentions_collections = db.ContentMentions
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def count_records(countType, params):
    if 'content_id' not in params:
        raise ValueError("Il parametro content_id è obbligatorio.")
    else:
        filter_params = {
            'content_id': params['content_id'],
        }

    if countType == 'Booked':
        collection = db.ContentBooked
        count = collection.count_documents(filter_params)

    elif countType == 'Discussion':
        collection = db.ContentDiscussion
        count = collection.count_documents(filter_params)

    elif countType == 'Like':
        collection = db.ContentLike
        count = collection.count_documents(filter_params)

    else:
        raise ValueError(f"countType '{countType}' non valido.")

    return count


def serialize_document(doc):
    """Converte ObjectId e altri tipi non serializzabili in stringhe."""
    if isinstance(doc, list):
        return [serialize_document(item) for item in doc]
    elif isinstance(doc, dict):
        return {key: serialize_document(value) for key, value in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
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

            # Recupera l'utente dal database usando t_username
            user = users_collection.find_one({"t_username": t_username})
            if not user:
                return func.HttpResponse(
                    "Utente non trovato.",
                    status_code=404
                )

            # Ottieni i parametri dalla query string
            content_id = req.params.get('id')
            if not content_id:
                return func.HttpResponse(
                    "Parametro id contenuto non fornito nella query string.",
                    status_code=400
                )

            # Verifica se il contenuto esiste
            content = content_collection.find_one({"_id": ObjectId(content_id)})
            if not content:
                return func.HttpResponse(
                    "Contenuto non trovato.",
                    status_code=404
                )

            maps = []
            reviews = []
            location = []

            if content.get("t_type") == "Eventi":
                # recupera le mappe
                maps = list(db.EventMaps.find({"t_map_event_id": ObjectId(content_id)}))
                for map_item in maps:
                    t_map_id = map_item.get("_id")
                    map_item["t_map_id"]=t_map_id
                    # Recupera gli oggetti della mappa
                    object_maps = list(db.ObjectMaps.find({"n_id_map": ObjectId(t_map_id)}))
                    for object_map in object_maps:
                        n_object_map_id = object_map.get("_id")
                        object_map["n_id"]=n_object_map_id
                        seat_list = list(db.ObjectSeats.find({"n_object_map_id": ObjectId(n_object_map_id)}))
                        object_map["t_seat_list"] = seat_list
                    map_item["t_object_maps"] = object_maps

                # Recupera le recensioni
                reviews = list(db.TicketReviews.find({"t_event_id": ObjectId(content_id)}))

                # Recupera la location
                location = db.EventLocation.find_one({"event_id": ObjectId(content_id)})

            content_tags = list(content_tags_collections.find({"content_id": ObjectId(content_id)}))
            content_mentions = list(content_mentions_collections.find({"content_id": ObjectId(content_id)}))

            # Recupera i dettagli dell'utente associato al contenuto
            content_user = users_collection.find_one({"t_alias_generated": content.get("t_alias_generated")})

            if not content_user:
                return func.HttpResponse(
                    "Utente associato al contenuto non trovato.",
                    status_code=404
                )

            # Prepara l'oggetto di risposta
            response_data = {
                "id": str(content.get('_id')),
                "t_caption": content.get('t_caption'),
                "t_image_link": content.get('t_image_link'),
                "t_video_link": content.get('t_video_link'),
                "t_user": {
                    "id": str(content_user.get('_id')),
                    "t_name": content_user.get('t_name'),
                    "t_follower_number": content_user.get('t_follower_number'),
                    "t_alias_generated": content_user.get('t_alias_generated'),
                    "t_description": content_user.get('t_description'),
                    "t_profile_photo": content_user.get('t_profile_photo'),
                    "t_type": content_user.get('t_type'),
                    "is_verified": content_user.get('is_verified', False),
                    "type": content_user.get('t_type')
                },
                "n_click": content.get('n_click'),
                "type": content.get('t_type'),
                "created_date": content.get('created_date'),
                "numOfComment": count_records("Discussion", {"content_id": ObjectId(content_id)}),
                "numOfLike": count_records("Like", {"content_id": ObjectId(content_id)}),
                "numOfBooked": count_records("Booked", {"content_id": ObjectId(content_id)}),
                "n_group_id": content.get("n_group_id") if content.get("t_type") == "Eventi" else None,
                "t_event_date": content.get("t_event_date") if content.get("t_type") == "Eventi" else None,
                "t_map_list": serialize_document(maps),
                "t_reviews": serialize_document(reviews),
                "t_location": serialize_document(location),
                "b_active": content.get("b_active"),
                "t_privacy": content.get("t_privacy"),
                "tags": serialize_document(content_tags),
                "mentions": serialize_document(content_mentions)
            }

            return func.HttpResponse(
                body=json.dumps(response_data),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse("Errore durante l'elaborazione della richiesta", status_code=500)

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo GET.",
            status_code=405
        )
