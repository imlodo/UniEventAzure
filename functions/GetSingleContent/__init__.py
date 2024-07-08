import logging
import os
import random
from datetime import datetime
import pymongo
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
contents_collection = db.Contents
users_collection = db.User

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def count_records(countType, params):
    if 'content_id' not in params:
        raise ValueError("Il parametro content_id è obbligatorio.")
    else:
        filter_params = {
            'content_id': str(params['content_id']),
        }

    if countType == 'Booked':
        collection = db.CONTENT_BOOKED
        count = collection.count_documents(filter_params)

    elif countType == 'Discussion':
        collection = db.CONTENT_DISCUSSION
        count = collection.count_documents(filter_params)

    elif countType == 'Like':
        collection = db.CONTENT_LIKE
        count = collection.count_documents(filter_params)

    else:
        raise ValueError(f"countType '{countType}' non valido.")

    return count


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
            # user = users_collection.find_one({"t_username": t_username})
            # if not user:
            #     return func.HttpResponse(
            #         "Utente non trovato.",
            #         status_code=404
            #     )

            # Ottieni i parametri dalla query string
            t_alias_generated = req.params.get('t_alias_generated')
            content_id = req.params.get('id')
            if not t_alias_generated or not content_id:
                return func.HttpResponse(
                    "Parametri t_alias_generated e id non forniti nella query string.",
                    status_code=400
                )

            # Verifica se il contenuto esiste
            #content = contents_collection.find_one({"id": int(content_id), "t_alias_generated": t_alias_generated})
            content = {
                "id": content_id,
                "t_caption": "Vetrina artistica",
                "t_image_link": "/assets/img/topic-image-placeholder.jpg",
                "t_topic_date": "2024-07-07T15:34:10.526Z",
                "t_alias_generated": t_alias_generated,
                "n_click": 6720272,
                "type": "Topics" if random.random() > 0.5 else "Eventi",
                "created_date": "2024-06-15T15:34:10.527Z"
            }
            if not content:
                return func.HttpResponse(
                    "Contenuto non trovato.",
                    status_code=404
                )

            # Recupera i dettagli dell'utente associato al contenuto
            #content_user = users_collection.find_one({"t_alias_generated": t_alias_generated})
            content_user = {
                "id": 456,
                "t_name": "Name 1",
                "t_follower_number": 1705,
                "t_alias_generated": "Alias1",
                "t_description": "Ti aiutiamo a diventare la versione migliore di TE STESSO! Seguici su Instagram.",
                "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                "t_type": 1,
                "is_verified": False,
                "type": "Utenti"
            }
            if not content_user:
                return func.HttpResponse(
                    "Utente associato al contenuto non trovato.",
                    status_code=404
                )

            # Prepara l'oggetto di risposta
            response_data = {
                "id": content.get('id'),
                "t_caption": content.get('t_caption'),
                "t_image_link": content.get('t_image_link'),
                "t_topic_date": content.get('t_topic_date'),
                "t_user": {
                    "id": content_user.get('id'),
                    "t_name": content_user.get('t_name'),
                    "t_follower_number": content_user.get('t_follower_number'),
                    "t_alias_generated": content_user.get('t_alias_generated'),
                    "t_description": content_user.get('t_description'),
                    "t_profile_photo": content_user.get('t_profile_photo'),
                    "t_type": content_user.get('t_type'),
                    "is_verified": content_user.get('is_verified', False),
                    "type": "Utenti"  # Puoi aggiungere logica per determinare il tipo
                },
                "n_click": content.get('n_click'),
                "type": content.get('type'),
                "created_date": content.get('created_date'),
                "numOfComment": random.randint(1, 10000),  #count_records("Discussion",{"content_id":content_id}),
                "numOfLike": random.randint(1, 10000),  #count_records("Like",{"content_id":content_id}),
                "numOfBooked": random.randint(1, 10000)  #count_records("Booked",{"content_id":content_id})
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
