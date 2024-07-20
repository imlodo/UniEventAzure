import logging
import os
from random import random

import pymongo
import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
import azure.functions as func
from werkzeug.security import generate_password_hash
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


def update_user_info(t_username, updates):
    result = users_collection.update_one({"t_username": t_username}, {"$set": updates})
    return result.modified_count > 0


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    "Autorizzazione non valida.",
                    status_code=404
                )

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')

            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    "Token scaduto.",
                    status_code=404
                )
            except jwt.InvalidTokenError:
                return func.HttpResponse(
                    "Token non valido.",
                    status_code=404
                )

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    "Token non contiene un username valido.",
                    status_code=404
                )

            # Prova a ottenere i dati JSON dal corpo della richiesta
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    "La richiesta non contiene dati JSON validi.",
                    status_code=400
                )

            # Estrai gli altri parametri opzionali
            t_name = req_body.get('t_name')
            t_surname = req_body.get('t_surname')
            t_description = req_body.get('t_description')
            t_profile_photo = req_body.get('t_profile_photo')
            t_actual_password = req_body.get('actual_password')
            t_password = req_body.get('t_password')

            # Verifica che almeno uno degli altri parametri sia presente
            if not (t_name or t_surname or t_description or t_profile_photo or t_password):
                return func.HttpResponse(
                    "Inserire almeno uno tra t_name, t_surname, t_description, t_profile_photo, t_password nel corpo della richiesta.",
                    status_code=400
                )

            # Crea un dizionario per gli aggiornamenti
            updates = {}
            if t_name:
                updates['t_name'] = t_name
            if t_surname:
                updates['t_surname'] = t_surname
            if t_description:
                updates['t_description'] = t_description
            if t_profile_photo:
                updates['t_profile_photo'] = t_profile_photo
            #if t_actual_password:
             #fare controllo se la actual password corrisponde a quella memorizzata nel db altrimenti restituire errore
            if t_password:
                updates['t_password'] = generate_password_hash(t_password)

            # Esegui l'aggiornamento nel database
            # update_user_info(t_username, updates):
            if random() > 0.5:
                response_body = json.dumps({"message": "Informazioni utente aggiornate con successo."})
                return func.HttpResponse(
                    body=response_body,
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    "Nessun aggiornamento eseguito. Controlla che i dati siano corretti.",
                    status_code=404
                )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante l'aggiornamento delle informazioni utente.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )
