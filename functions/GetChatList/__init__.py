import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import azure.functions as func
import jwt

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

        #Recupera i messaggi dal database
        messages = messages_collection.find(
            {"$or": [{"user_at": username}, {"user_from": username}]}
        )

        # Creazione di un dizionario per tracciare gli utenti unici e l'ultimo messaggio
        unique_users = {}
        for message in messages:
            # Recupera i dettagli dell'utente dal database degli utenti
            user_at = users_collection.find_one({"username": message["user_at"]})
            user_from = users_collection.find_one({"username": message["user_from"]})

            if not user_at or not user_from:
                continue

            user_key = user_at["alias_generated"] if user_at["username"] != username else user_from["alias_generated"]
            if user_key not in unique_users:
                unique_users[user_key] = {
                    "userChat": {
                        "t_name": user_at["name"] if user_at["username"] != username else user_from["name"],
                        "t_surname": user_at["surname"] if user_at["username"] != username else user_from["surname"],
                        "t_alias_generated": user_key,
                        "t_profile_photo": user_at.get("profile_photo") if user_at["username"] != username else user_from.get("profile_photo"),
                        "t_type": user_at["type"] if user_at["username"] != username else user_from["type"]
                    },
                    "messages": [{
                        "user_at": user_at,
                        "user_from": user_from,
                        "message": message["message"],
                        "dateTime": message["dateTime"]
                    }]
                }
            else:
                # Aggiorna con l'ultimo messaggio se è più recente
                if message["dateTime"] > unique_users[user_key]["messages"][0]["dateTime"]:
                    unique_users[user_key]["messages"][0] = {
                        "user_at": user_at,
                        "user_from": user_from,
                        "message": message["message"],
                        "dateTime": message["dateTime"]
                    }

        # Creazione della lista di utenti per la risposta
        user_list = list(unique_users.values())

        # Ordinamento della lista in base agli ultimi utenti scritti
        user_list = sorted(user_list, key=lambda x: x["messages"][0]["dateTime"], reverse=True)

        response_body = json.dumps(user_list, default=str)
        return func.HttpResponse(response_body, mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return func.HttpResponse("Si è verificato un errore durante il recupero delle chat.", status_code=500)
