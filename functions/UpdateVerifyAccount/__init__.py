import logging
import os
from datetime import datetime

import pymongo
from bson import ObjectId
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

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

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

            # Ottieni il ruolo dell'utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    "Token non contiene un utente valido.",
                    status_code=401
                )

            user = users_collection.find_one({"t_username": t_username})

            #Controlla il ruolo dell'utente
            if user.get("t_role") == "Utente":
                return func.HttpResponse(
                    "Non autorizzato a modificare lo stato delle richieste.",
                    status_code=403
                )

            # Prova a ottenere i dati JSON dal corpo della richiesta
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    "La richiesta non contiene dati JSON validi.",
                    status_code=400
                )

            # Estrai i campi dal corpo della richiesta
            request_id = req_body.get('request_id')
            t_state = req_body.get('t_state')
            t_motivation = req_body.get('t_motivation')

            # Controlla che i campi obbligatori siano presenti
            if not (request_id and t_state):
                return func.HttpResponse(
                    "ID richiesta e stato sono obbligatori.",
                    status_code=400
                )

            #Trova la richiesta di verifica
            verify_request = user_verify_collection.find_one({"_id": ObjectId(request_id)})

            if not verify_request:
                return func.HttpResponse(
                    "Richiesta di verifica non trovata.",
                    status_code=404
                )

            # Aggiorna lo stato della richiesta
            if t_state == "refused":
                update_fields = {
                    "status": t_state,
                    "refused_date": datetime.now().date().isoformat(),
                    "refused_motivation": t_motivation
                }
            elif t_state == "verified":
                update_fields = {
                    "status": t_state
                }
                #Aggiorna anche il t_type dell'utente
                users_collection.update_one(
                    {"t_username": verify_request.get("t_username")},
                    {"$set": {"t_type": "ARTIST", "is_verified": True}}
                )
            else:
                return func.HttpResponse(
                    "Stato non valido.",
                    status_code=400
                )

            # Esegui l'aggiornamento della richiesta
            user_verify_collection.update_one({"_id": ObjectId(request_id)}, {"$set": update_fields})

            return func.HttpResponse(
                json.dumps({"message": "Stato della richiesta aggiornato con successo."}, default=json_serial),
                status_code=200,
                mimetype="application/json"
            )

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse("Errore durante l'elaborazione della richiesta", status_code=500)

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )
