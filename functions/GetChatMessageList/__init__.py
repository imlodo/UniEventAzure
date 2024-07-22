import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import azure.functions as func
import jwt
import json

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Ottieni la stringa di connessione dal file delle variabili d'ambiente
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione per i messaggi e gli utenti
messages_collection = db.Messages
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Ottieni il token JWT dall'header Authorization
        auth_header = req.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return func.HttpResponse("Autorizzazione non valida.", status_code=401)

        jwt_token = auth_header.split(' ')[1]

        # Decodifica il token JWT
        secret_key = os.getenv('JWT_SECRET_KEY')
        try:
            decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return func.HttpResponse("Token scaduto.", status_code=401)
        except jwt.InvalidTokenError:
            return func.HttpResponse("Token non valido.", status_code=401)

        # Ottieni l'username dal token decodificato
        username = decoded_token.get('username')
        if not username:
            return func.HttpResponse("Token non contiene un username valido.", status_code=401)

        # Ottieni l'alias dell'utente target dai parametri della richiesta
        target_alias = req.params.get('target_alias')
        if not target_alias:
            return func.HttpResponse("Alias target non fornito.", status_code=400)

        # Recupera i messaggi dal database per l'utente corrente e l'utente target
        messages = messages_collection.find(
            {"$or": [
                {"$and": [{"user_to": username}, {"user_at": target_alias}]},
                {"$and": [{"user_at": username}, {"user_to": target_alias}]}
            ]}
        ).sort("dateTime", -1)

        # Creazione della lista dei messaggi
        messages_list = []
        for message in messages:
            user_to = users_collection.find_one({"username": message["user_to"]})
            user_at = users_collection.find_one({"username": message["user_at"]})

            if not user_to or not user_at:
                continue

            messages_list.append({
                "user_to": user_to,
                "user_at": user_at,
                "message": message["message"],
                "dateTime": message["dateTime"]
            })

        response_body = json.dumps(messages_list, default=str)
        return func.HttpResponse(response_body, mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return func.HttpResponse("Si è verificato un errore durante il recupero dei messaggi.", status_code=500)
