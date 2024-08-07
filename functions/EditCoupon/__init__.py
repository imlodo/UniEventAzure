import logging
import os
import pymongo
from bson import ObjectId
from pymongo import MongoClient
import azure.functions as func
import json
import jwt

# Connessione al cluster di Azure Cosmos DB for MongoDB
connect_string = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connect_string)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
content_collection = db.Contents
users_collection = db.Users
coupons_collection = db.EventCoupon

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        try:
            token = req.headers.get('Authorization')
            if not token:
                return func.HttpResponse("Token mancante.", status_code=401)

            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse("Autorizzazione non valida.", status_code=401)

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')

            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse("Token scaduto.", status_code=401)
            except jwt.InvalidTokenError:
                return func.HttpResponse("Token non valido.", status_code=401)

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse("Token non contiene un username valido.", status_code=401)

            # Ottieni il corpo della richiesta
            req_body = req.get_json()
            coupon_id = req_body.get('coupon_id')
            coupon_code = req_body.get('coupon_code')
            discount = req_body.get('discount')
            content_id = req_body.get('content_id')

            if not coupon_id or not coupon_code or not discount or not content_id:
                return func.HttpResponse("Dati incompleti nel corpo della richiesta.", status_code=400)

            #Trova l'utente
            user = users_collection.find_one({"t_username": t_username})
            if not user:
                return func.HttpResponse("Utente non trovato.", status_code=404)

            t_alias_generated = user.get('t_alias_generated')

            # Trova il contenuto
            content = content_collection.find_one({"_id": ObjectId(content_id), "t_alias_generated": t_alias_generated})
            if not content:
                return func.HttpResponse("Contenuto non trovato o l'utente non è autorizzato.", status_code=404)

            # Trova il coupon
            coupon = coupons_collection.find_one({"_id": ObjectId(coupon_id), "event_id": ObjectId(content_id)})
            if not coupon:
                return func.HttpResponse("Coupon non trovato per il contenuto specificato.", status_code=404)

            # Modifica il coupon
            coupons_collection.update_one(
                {"_id": ObjectId(coupon_id)},
                {"$set": {"coupon_code": coupon_code, "discount": discount}}
            )

            coupon = coupons_collection.find_one({"_id": ObjectId(coupon_id), "event_id": ObjectId(content_id)})

            return func.HttpResponse(
                json.dumps({"coupon": coupon}, default=str),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante la modifica del coupon.", status_code=500)

    else:
        return func.HttpResponse(status_code=404)
