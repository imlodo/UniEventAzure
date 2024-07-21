import logging
import os
from datetime import datetime
from random import random

import jwt
import json
from dotenv import load_dotenv
from pymongo import MongoClient
import azure.functions as func

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione USERS
users_collection = db.Users

# Seleziona la collezione CONTENT_BOOKED
content_like_collection = db.ContentLike

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

            # Estrai t_alias_generated_from e t_alias_generated_to dal corpo della richiesta
            t_alias_generated = req_body.get('t_alias_generated')
            content_id = req_body.get('content_id')
    
            if not t_alias_generated or not content_id:
                return func.HttpResponse(
                    "I parametri t_alias_generated e content_id sono obbligatori.",
                    status_code=400
                )
    
            # Recupera l'utente dal t_alias_generated
            #user = users_collection.find_one({"t_alias_generated": t_alias_generated})
    
            # if not user:
            #     return func.HttpResponse(
            #         "Utente non trovato.",
            #         status_code=404
            #     )
    
            t_username = "baldi"  #user.get('username')

            # Verifica se l'utente 'from' segue l'utente 'to'
            #liked_record = content_like_collection.find_one({"content_id": content_id, "t_username": t_username})

            # if liked_record:
            #     return func.HttpResponse(
            #         body=json.dumps({"liked": True, "message": "L'utente ha lasciato un like per il contenuto"}),
            #         status_code=200,
            #         mimetype='application/json'
            #     )
            # else :
            #     return func.HttpResponse(
            #         body=json.dumps({"liked": False, "message": "L'utente non ha lasciato like per il contenuto"}),
            #         status_code=200,
            #         mimetype='application/json'
            #     )
                
            if random() > 0.5:
                return func.HttpResponse(
                    body=json.dumps({"liked": True, "message": "L'utente ha lasciato un like per il contenuto"}),
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    body=json.dumps({"liked": False, "message": "L'utente non ha lasciato un like per il contenuto"}),
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
