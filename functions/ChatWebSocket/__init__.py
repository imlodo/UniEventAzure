import hashlib
import logging
import os
import pymongo
import jwt
from pymongo import MongoClient
from datetime import datetime
import azure.functions as func
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def get_user_info_by_username(t_username):
    user = users_collection.find_one({"t_username": t_username})
    if user:
        # Rimuovi l'ID se presente (per esempio, se è un ObjectId)
        if '_id' in user:
            del user['_id']
        # Rimuovi il campo password se presente (per sicurezza)
        if 't_password' in user:
            del user['t_password']
        return user
    return None


def get_user_info_by_alias(alias):
    user = users_collection.find_one({"t_alias_generated": alias})
    if user:
        # Rimuovi l'ID se presente (per esempio, se è un ObjectId)
        if '_id' in user:
            del user['_id']
        # Rimuovi il campo password se presente (per sicurezza)
        if 't_password' in user:
            del user['t_password']
        return user
    return None

def main(request, actions: func.Out[str]) -> None:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info(request)
    try:
        # Ottieni il corpo della richiesta
        data_json = json.loads(request)
        request_json = json.loads(data_json["data"])
        logging.info(request_json)
    except ValueError:
        logging.error("Invalid JSON in request body.")
        return

    logging.info(request_json["token"])
    # Estrai il token dal messaggio
    jwt_token = request_json.get('token')
    if not jwt_token:
        logging.error("Missing token.")
        return

    # Decodifica il token JWT
    secret_key = os.getenv('JWT_SECRET_KEY')
    try:
        decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        logging.error("Token expired.")
        return
    except jwt.InvalidTokenError:
        logging.error("Invalid token.")
        return

    # Ottieni l'ID utente dal token decodificato
    t_username = decoded_token.get('username')
    if not t_username:
        logging.error("Invalid token payload.")
        return

    #Ottieni l'utente completo (user_from) dal token
    user_from = get_user_info_by_username(t_username)
    if not user_from:
        logging.error("User not found.")
        return

    # Ottieni i dettagli del messaggio
    t_alias_generated = request_json.get('t_alias_generated')
    message_content = request_json.get('content')

    if not t_alias_generated or not message_content:
        logging.error("Missing required fields.")
        return

    #Ottieni l'utente completo (user_to) dall'alias generato
    user_to = get_user_info_by_alias(t_alias_generated)
    if not user_to:
        logging.error("Recipient user not found.")
        return

    # Aggiungi la data di creazione corrente
    creation_date = datetime.utcnow().isoformat()

    # Costruisci l'oggetto da inviare
    message_object = {
        "user_from": user_from,
        "user_at": user_to,
        "message": message_content,
        "dateTime": creation_date
    }
    
    # Invia il messaggio a tutti i client in ascolto
    actions.set(json.dumps({
        "actionName": "sendToAll",
        "data": json.dumps(message_object),
        "dataType": "json"
    }))
