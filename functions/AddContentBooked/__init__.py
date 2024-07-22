import json
import logging
import os
from enum import Enum
from random import random

import pymongo
from pymongo import MongoClient
import azure.functions as func
import jwt
from functools import wraps
from datetime import datetime

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione USERS
users_collection = db.Users

# Seleziona la collezione CONTENT_BOOKED
content_booked_collection = db.ContentBooked

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Enum per i ruoli utente
class USER_ROLE(Enum):
    UTENTE = "Utente"
    MODERATORE = "Moderatore"
    SUPERMODERATORE = "Super Moderatore"


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
        user = users_collection.find_one({"t_username": t_username})
        if not user:
            return func.HttpResponse(
                "Utente non trovato.",
                status_code=404
            )

        req_body = req.get_json()
        t_alias_generated = req_body.get('t_alias_generated')
        content_id = req_body.get('content_id')

        if not t_alias_generated or not content_id:
            return func.HttpResponse(
                "I parametri t_alias_generated e content_id sono obbligatori.",
                status_code=400
            )

        # Recupera l'utente dal t_alias_generated
        user = users_collection.find_one({"t_alias_generated": t_alias_generated})

        if not user:
            return func.HttpResponse(
                "Utente non trovato.",
                status_code=404
            )

        t_username = user.get('username')

        existing_record = content_booked_collection.find_one({"content_id": content_id, "t_username": t_username})
        if existing_record:
            content_booked_collection.delete_one({"content_id": content_id, "t_username": t_username})
            return func.HttpResponse(
                body=json.dumps({"booked": False,"message": "Contenuto rimosso dai preferiti"}),
                status_code=201,
                mimetype='application/json'
            )

        # Crea un nuovo record nella tabella CONTENT_BOOKED
        new_record = {
            "content_id": content_id,
            "t_username": t_username,
            "created_at": datetime.utcnow()
        }

        content_booked_collection.insert_one(new_record)
        return func.HttpResponse(
            body=json.dumps({"booked": True, "message": "Contenuto aggiunto ai preferiti"}),
            status_code=201,
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
        return func.HttpResponse(
            "Errore durante l'elaborazione della richiesta.",
            status_code=500
        )
