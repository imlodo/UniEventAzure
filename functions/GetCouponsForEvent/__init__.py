import logging
import os
import json
import jwt
from datetime import datetime

import pymongo
from azure.functions import HttpResponse
from pymongo import MongoClient
import azure.functions as func

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
event_coupon_collection = db.EventCoupon
user_collection = db.Users
event_collection = db.Contents

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def get_user_alias_from_token(token):
    """Estrai l'alias dell'utente dal token JWT."""
    secret_key = os.getenv('JWT_SECRET_KEY')

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded_token.get('t_alias_generated')
    except jwt.ExpiredSignatureError:
        raise ValueError("Token scaduto.")
    except jwt.InvalidTokenError:
        raise ValueError("Token non valido.")


def get_event_creator_alias(event_id):
    """Recupera l'alias dell'utente che ha creato l'evento."""
    event = event_collection.find_one({"event_id": event_id})
    if event:
        return event.get("t_alias_generated")
    return None


def get_coupons_for_event(event_id):
    """Recupera i coupon associati all'evento."""
    coupons = event_coupon_collection.find({"event_id": event_id})
    return list(coupons)


def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
        try:
            # Recupera il token e l'ID dell'evento dalla richiesta
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return HttpResponse("Autorizzazione non valida.", status_code=401)

            token = auth_header.split(' ')[1]
            event_id = req.params.get('id')
            if not event_id:
                return HttpResponse("ID evento mancante.", status_code=400)

            # Decodifica il token e ottieni l'alias dell'utente
            try:
                user_alias = get_user_alias_from_token(token)
            except ValueError as e:
                return HttpResponse(str(e), status_code=401)

            # Verifica se l'utente è l'autore dell'evento
            event_creator_alias = get_event_creator_alias(event_id)
            if event_creator_alias != user_alias:
                return HttpResponse("Utente non autorizzato a visualizzare i coupon per questo evento.", status_code=403)

            # Recupera i coupon per l'evento
            coupons = get_coupons_for_event(event_id)
            response_body = json.dumps({"coupons": coupons})

            return HttpResponse(
                body=response_body,
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Si è verificato un errore: {e}")
            return HttpResponse(
                "Si è verificato un errore durante il recupero dei coupon.",
                status_code=500
            )

    else:
        return HttpResponse(
            status_code=404
        )
