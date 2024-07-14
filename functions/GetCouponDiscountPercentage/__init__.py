import logging
import os
from datetime import datetime, timedelta
from enum import Enum

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
event_coupon_collection = db.EventCoupon

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

            # Ottieni il buy token dall'header Buy-Token
            buy_token = req.headers.get('Buy-Token')
            if not buy_token or not buy_token.startswith('Bearer '):
                return func.HttpResponse(
                    "Buy token non valido.",
                    status_code=401
                )

            buy_jwt_token = buy_token.split(' ')[1]

            # Decodifica i token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')

            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
                decoded_buy_token = jwt.decode(buy_jwt_token, secret_key, algorithms=['HS256'])
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

            # Ottieni i parametri dalla query string
            event_id = req.params.get('event_id')
            coupon_code = req.params.get('coupon_code')
            if not event_id or not coupon_code:
                return func.HttpResponse(
                    "Parametri event_id e coupon_code mancanti nella query string.",
                    status_code=400
                )

            # Cerca il coupon nel database
            #coupon = event_coupon_collection.find_one({"event_id": event_id, "coupon_code": coupon_code})
            coupon = None
            if coupon_code == "SUMMER21":
                coupon = {
                    "coupon_id":"asdasda7338322",
                    "event_id": "event123",
                    "coupon_code": "SUMMER21",
                    "discount": 20
                }

            if coupon:
                # Prepara la risposta
                coupon_data = {
                    "coupon_id": str(coupon.get('_id')), 
                    "event_id": coupon.get('event_id'),
                    "coupon_code": coupon.get('coupon_code'),
                    "discount": coupon.get('discount')
                }
                return func.HttpResponse(
                    body=json.dumps(coupon_data),
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    "Coupon non trovato.",
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
