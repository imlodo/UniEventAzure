import logging
import os
import pymongo
import jwt
from azure.functions import HttpResponse
from pymongo import MongoClient
from datetime import datetime, timedelta
import azure.functions as func
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = ("mongodb://unieventcosmosdb"
                 ":a1MoJYXGpXTf2Rgz1KoFFrMnlxLSEnyZmQ5f5WhQeXt1B99VN1LkKmllq2sIN4ueFA0ZevjRhQjZACDbwgZgDA"
                 "==@unieventcosmosdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb"
                 "&maxIdleTimeMS=120000&appName=@unieventcosmosdb@")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
users_collection = db.User

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


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Controlla che il metodo della richiesta sia GET
    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    status_code=404
                )

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.environ.get('JWT_SECRET_KEY', '96883c431142be979c69509655c4eca623a34714f948206b0cfbed0e986b173e')
            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    status_code=404
                )
            except jwt.InvalidTokenError:
                return func.HttpResponse(
                    status_code=404
                )

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    status_code=404
                )

            # Ottieni le informazioni complete dell'utente dal database
            user_info = get_user_info_by_username(t_username)

            if user_info:
                # Costruisci il corpo della risposta come oggetto JSON senza 't_password' e '_id'
                user_response = { "user": user_info }
                response_body = json.dumps(user_response)

                return func.HttpResponse(
                    body=response_body,
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    status_code=404
                )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero delle informazioni utente.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            status_code=404
        )
