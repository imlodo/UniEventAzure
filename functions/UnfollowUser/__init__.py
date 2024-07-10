import logging
import os
from datetime import datetime
import jwt

import pymongo
import azure.functions as func
import json
from dotenv import load_dotenv
from pymongo import MongoClient

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Ottieni la stringa di connessione dal file delle variabili d'ambiente
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
follow_user_collection = db.FollowUser
users_collection = db.User

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Controlla che il metodo della richiesta sia POST
    if req.method == 'POST':
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
            # Prova a ottenere i dati JSON dal corpo della richiesta
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    "La richiesta non contiene dati JSON validi.",
                    status_code=400
                )

            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    "Token non contiene un username valido.",
                    status_code=401
                )

            # user = users_collection.find_one({"t_username": t_username})
            # if not user:
            #     return func.HttpResponse(
            #         "Utente non trovato.",
            #         status_code=404
            #     )

            # Estrai t_alias_generated_from e t_alias_generated_to dal corpo della richiesta
            t_alias_generated_to = req_body.get('t_alias_generated_to')

            if not t_alias_generated_to:
                return func.HttpResponse(
                    "Inserire t_alias_generated_to nel corpo della richiesta.",
                    status_code=400
                )

            # Inserimento del nuovo record nella collezione FollowUser
            #result = follow_user_collection.delete_one({
            #   "t_alias_generated_from": user.get("t_alias_generated"),
            #  "t_alias_generated_to": t_alias_generated_to
            #})
            # if result.deleted_count > 0 :
            #     return func.HttpResponse(
            #         body=json.dumps({"message": "Unfollow dell'utente eseguito con successo."}),
            #         status_code=200,
            #         mimetype='application/json'
            #     )
            # else:
            #     return func.HttpResponse(
            #         body=json.dumps({"message": "Unfollow dell'utente non riuscito"}),
            #         status_code=400,
            #         mimetype='application/json'
            #     )
            return func.HttpResponse(
                body=json.dumps({"message": "Unfollow dell'utente eseguito con successo."}),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante l'operazione.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )
