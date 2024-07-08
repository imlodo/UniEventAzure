import json
import logging
import os
import random
from enum import Enum

import pymongo
from pymongo import MongoClient
import azure.functions as func
import jwt
from functools import wraps

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Enum per i ruoli utente
class USER_ROLE(Enum):
    UTENTE = "Utente"
    MODERATORE = "Moderatore"
    SUPERMODERATORE = "Super Moderatore"


def count_records(countType, params):
    if 'content_id' not in params:
        raise ValueError("Il parametro content_id è obbligatorio.")
    elif 'discussion_id' not in params:
        filter_params = {
            'content_id': int(params['content_id']),
        }
    else:
        filter_params = {
            'content_id': int(params['discussion_id']),
        }

    if countType == 'Booked':
        collection = db.CONTENT_BOOKED
        count = collection.count_documents(filter_params)

    elif countType == 'Discussion':
        collection = db.CONTENT_DISCUSSION
        count = collection.count_documents(filter_params)

    elif countType == 'LikeContent':
        collection = db.CONTENT_LIKE
        count = collection.count_documents(filter_params)

    elif countType == 'LikeDiscussion':
        collection = db.DISCUSSION_LIKE
        count = collection.count_documents(filter_params)

    else:
        raise ValueError(f"countType '{countType}' non valido.")

    return count


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

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

        countType = req.params.get('countType')
        params = {
            'content_id': req.params.get('content_id'),
            'discussion_id': req.params.get('discussion_id')
        }

        if not countType:
            return func.HttpResponse(
                "Parametro countType non fornito nella query string.",
                status_code=400
            )

        # Esegui il conteggio in base al countType e ai parametri forniti
        count = random.randint(1, 10000)  #count_records(countType, params)

        response_data = {
            "count": count
        }

        return func.HttpResponse(
            body=json.dumps(response_data),
            status_code=200,
            mimetype='application/json'
        )

    except ValueError as ve:
        logging.error(f"Errore: {ve}")
        return func.HttpResponse(
            str(ve),
            status_code=400
        )
    except Exception as e:
        logging.error(f"Errore: {e}")
        return func.HttpResponse("Errore durante l'elaborazione della richiesta", status_code=500)
