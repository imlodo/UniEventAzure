import logging
import os
from datetime import datetime, timedelta
from enum import Enum
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

# Seleziona la collezione (crea la collezione se non esiste)
user_verify_collection = db.UserVerify
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Enum per il ruolo dell'utente
class USER_ROLE(Enum):
    UTENTE = "Utente"
    MODERATORE = "Moderatore"
    SUPERMODERATORE = "Super Moderatore"


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

            # # Recupera l'utente dal database usando t_username
            # user = users_collection.find_one({"t_username": t_username})
            # if not user:
            #     return func.HttpResponse(
            #         "Utente non trovato.",
            #         status_code=404
            #     )
            # 
            # # Verifica il ruolo dell'utente
            # user_role = user.get('t_role')
            # if user_role not in [USER_ROLE.MODERATORE.value, USER_ROLE.SUPERMODERATORE.value]:
            #     return func.HttpResponse(
            #         "Permessi insufficienti.",
            #         status_code=403
            #     )

            # Ottieni l'username dalla query string
            query_alias = req.params.get('t_alias_generated')
            if not query_alias:
                return func.HttpResponse(
                    "Username non fornito nella query string.",
                    status_code=400
                )

            #request_user = users_collection.find_one({"t_alias_generated": query_alias})
            # Verifica se l'utente esiste
            #user_verify = user_verify_collection.find_one({"t_username": request_user.get("t_username")})
            user_verify = {"id":"test"}
            if user_verify:
                # Prepara la risposta
                # user_data = {
                #     "t_username": user_verify.get('t_username'),
                #     "name": user_verify.get('name'),
                #     "surname": user_verify.get('surname'),
                #     "birthdate": user_verify.get('birthdate'),
                #     "pIva": user_verify.get('pIva'),
                #     "companyName": user_verify.get('companyName'),
                #     "companyAddress": user_verify.get('companyAddress'),
                #     "pec": user_verify.get('pec'),
                #     "consentClauses": user_verify.get('consentClauses'),
                #     "identity_document": user_verify.get('identity_document'),
                #     "status": user_verify.get('status'),
                #     "refused_date": user_verify.get('refused_date')
                # }

                randomNumber = random()
                user_data = {
                    "status": "verified" if (1 >= randomNumber >= 0.8) else "requested" if (
                                0.8 >= randomNumber >= 0.6) else "refused" if (
                                0.6 >= randomNumber >= 0.5) else "not-verified"
                }
                return func.HttpResponse(
                    body=json.dumps(user_data),
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    "Utente non trovato.",
                    status_code=404
                )

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse("Errore durante l'elaborazione della richiesta", status_code=500)

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo GET.",
            status_code=405
        )
