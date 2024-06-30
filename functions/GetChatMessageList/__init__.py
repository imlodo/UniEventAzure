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

# Seleziona la collezione per i messaggi
messages_collection = db.Messages

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
        # messages = messages_collection.find(
        #     {"$or": [
        #         {"$and": [{"user_to.t_username": username}, {"user_at.t_alias_generated": target_alias}]},
        #         {"$and": [{"user_at.t_username": username}, {"user_to.t_alias_generated": target_alias}]}
        #     ]}
        # ).sort("dateTime", -1)
        # 
        # # Creazione della lista dei messaggi
        # messages_list = []
        # for message in messages:
        #     messages_list.append({
        #         "user_to": message["user_to"],
        #         "user_at": message["user_at"],
        #         "message": message["message"],
        #         "dateTime": message["dateTime"]
        #     })
        messages_list = [
            {
                "user_from": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "user_at": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "message": "Ciao Marco!",
                "dateTime": "2024-06-20T10:30:00Z"
            },
            {
                "user_from": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "user_at": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "message": "Ciao Luca!",
                "dateTime": "2024-06-20T11:00:00Z"
            },
            {
                "user_from": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "user_at": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "message": "Come stai?",
                "dateTime": "2024-06-21T10:30:00Z"
            },
            {
                "user_from": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "user_at": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "message": "Sto bene, grazie!",
                "dateTime": "2024-06-21T11:00:00Z"
            },
            {
                "user_from": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "user_at": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "message": "Hai visto l'ultimo film?",
                "dateTime": "2024-06-22T10:30:00Z"
            },
            {
                "user_from": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "user_at": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "message": "Sì, è stato fantastico!",
                "dateTime": "2024-06-22T11:00:00Z"
            },
            {
                "user_from": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "user_at": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "message": "Hai novità?",
                "dateTime": "2024-06-23T10:30:00Z"
            },
            {
                "user_from": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "user_at": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "message": "Niente di nuovo!",
                "dateTime": "2024-06-23T11:00:00Z"
            },
            {
                "user_from": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "user_at": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "message": "Andiamo a bere qualcosa stasera?",
                "dateTime": "2024-06-24T10:30:00Z"
            },
            {
                "user_from": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": target_alias,
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "user_at": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "message": "Certo, ci vediamo alle 8!",
                "dateTime": "2024-06-24T11:00:00Z"
            }
        ]
        response_body = json.dumps(messages_list, default=str)
        return func.HttpResponse(response_body, mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return func.HttpResponse("Si è verificato un errore durante il recupero dei messaggi.", status_code=500)
