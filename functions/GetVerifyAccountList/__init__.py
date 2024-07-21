import logging
import os
from datetime import datetime, timedelta
from random import random

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

# Seleziona le collezioni
user_verify_collection = db.UserVerify
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


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

            # Ottieni il ruolo dell'utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    "Token non contiene un utente valido.",
                    status_code=401
                )

            # Verifica l'utente nella collezione USERS
            # user = users_collection.find_one({"t_username": t_username})
            # if not user:
            #     return func.HttpResponse(
            #         "Utente non trovato.",
            #         status_code=404
            #     )
            
            user = {"t_role":"Moderatore"}

            # Controlla il ruolo dell'utente
            if user.get("t_role") != "Utente":
                all_requests = [
                    {
                        "_id": "60d5ec49d2a4b833b4e5e935",
                        "t_alias_generated": "jdoe",
                        "name": "John",
                        "surname": "Doe",
                        "birthdate": "1990-01-01",
                        "pIva": "12345678901",
                        "companyName": "Doe Enterprises",
                        "companyAddress": "123 Main Street, Cityville",
                        "pec": "jdoe@example.com",
                        "consentClauses": True,
                        "identity_document": ["https://rivieraticket.it/wp-content/uploads/2023/08/Tropical-closing-party-Byblos-01-09-23.jpg","https://rivieraticket.it/wp-content/uploads/2023/08/Tropical-closing-party-Byblos-01-09-23.jpg"],
                        "status": "requested",
                        "refused_date": None,
                        "refused_motivation": None
                    },
                    {
                        "_id": "60d5ec49d2a4b833b4e5e936",
                        "t_alias_generated": "asmith",
                        "name": "Alice",
                        "surname": "Smith",
                        "birthdate": "1985-05-15",
                        "pIva": "98765432109",
                        "companyName": "Smith Co.",
                        "companyAddress": "456 Market Street, Townsville",
                        "pec": "asmith@example.com",
                        "consentClauses": True,
                        "identity_document": ["https://rivieraticket.it/wp-content/uploads/2023/08/Tropical-closing-party-Byblos-01-09-23.jpg","https://rivieraticket.it/wp-content/uploads/2023/08/Tropical-closing-party-Byblos-01-09-23.jpg"],
                        "status": "refused",
                        "refused_date": "2023-03-01",
                        "refused_motivation": "Documenti non conformi"
                    },
                    {
                        "_id": "60d5ec49d2a4b833b4e5e937",
                        "t_alias_generated": "bwilson",
                        "name": "Bob",
                        "surname": "Wilson",
                        "birthdate": "1978-07-23",
                        "pIva": "56789012345",
                        "companyName": "Wilson Ltd.",
                        "companyAddress": "789 Park Avenue, Metropolis",
                        "pec": "bwilson@example.com",
                        "consentClauses": True,
                        "identity_document": ["https://rivieraticket.it/wp-content/uploads/2023/08/Tropical-closing-party-Byblos-01-09-23.jpg","https://rivieraticket.it/wp-content/uploads/2023/08/Tropical-closing-party-Byblos-01-09-23.jpg"],
                        "status": "verified",
                        "refused_date": None,
                        "refused_motivation": None
                    }
                ]
                # Ottieni tutte le richieste dalla collezione USER_VERIFY
                # all_requests = list(user_verify_collection.find())
                # 
                # # Aggiungi t_alias_generated per ogni richiesta
                # for request in all_requests:
                #     request['_id'] = str(request['_id'])  # Converti ObjectId in stringa
                #     # Recupera t_alias_generated dalla collezione USERS
                #     associated_user = users_collection.find_one({"t_username": request.get('t_username')})
                #     if associated_user:
                #         request['t_alias_generated'] = associated_user.get('t_alias_generated', 'Alias non trovato')
                #     else:
                #         request['t_alias_generated'] = 'Alias non trovato'

                return func.HttpResponse(json.dumps(all_requests), status_code=200, mimetype="application/json")
            else:
                return func.HttpResponse(
                    "Non autorizzato a visualizzare le richieste.",
                    status_code=403
                )

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse("Errore durante l'elaborazione della richiesta", status_code=500)

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo GET.",
            status_code=405
        )
