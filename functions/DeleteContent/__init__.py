import logging
import os
import random

import pymongo
from pymongo import MongoClient
import azure.functions as func
import json
import jwt

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
content_collection = db.Contents
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

#nella delete content devi cancellare anche tutte le cose collegate (es. i coupon, i commenti e così via)
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'DELETE':
        try:
            token = req.headers.get('Authorization')
            if not token:
                return func.HttpResponse("Token mancante.", status_code=401)

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

            # Ottieni il corpo della richiesta
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    "Richiesta non contiene un corpo JSON valido.",
                    status_code=400
                )

            content_id = req_body.get('content_id')

            # Ottieni il contenuto e l'utente creatore
            content = content_collection.find_one({"_id": content_id})
            if not content:
                return func.HttpResponse(
                    "Contenuto non trovato.",
                    status_code=404
                )

            user = users_collection.find_one({"t_username": t_username})
            if not user:
                return func.HttpResponse(
                    "Utente non trovato.",
                    status_code=404
                )

            # # Controlla se l'utente è il creatore del contenuto
            if content.get('t_alias_generated') != user.get('t_alias_generated'):
                return func.HttpResponse(
                    "L'utente non è autorizzato a cancellare questo contenuto.",
                    status_code=403
                )

            # Cancella il contenuto
            result = content_collection.delete_one({"_id": content_id})

            if result.deleted_count == 1:
                return func.HttpResponse(
                    json.dumps({"message": "Contenuto cancellato con successo."}),
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    "Errore nella cancellazione del contenuto.",
                    status_code=500
                )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante la cancellazione del contenuto.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            status_code=404
        )
