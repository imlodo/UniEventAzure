import logging
import os
import pymongo
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
users_collection = db.User
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
            coupon_code = req_body.get('coupon_code')
            discount = req_body.get('discount')
            content_id = req_body.get('content_id')

            if not coupon_code or not discount or not content_id:
                return func.HttpResponse("Dati incompleti nel corpo della richiesta.", status_code=400)

            # Trova l'utente
            # user = users_collection.find_one({"t_username": t_username})
            # if not user:
            #     return func.HttpResponse("Utente non trovato.", status_code=404)
            # 
            # t_alias_generated = user.get('t_alias_generated')
            # 
            # # Trova il contenuto
            # content = content_collection.find_one({"_id": content_id, "t_alias_generated": t_alias_generated})
            # if not content:
            #     return func.HttpResponse("Contenuto non trovato o l'utente non è autorizzato.", status_code=404)
            # 
            # # Aggiungi il coupon
            # new_coupon = {
            #     "coupon_id": str(pymongo.collection.ObjectId()),
            #     "event_id": content_id,
            #     "coupon_code": coupon_code,
            #     "discount": discount
            # }
            # 
            #coupon = coupons_collection.insert_one(new_coupon)

            coupon = {"coupon_id": "AASDASD3121", "event_id": content_id, "coupon_code": coupon_code,
                      "discount": discount}
            return func.HttpResponse(
                json.dumps({"coupon": coupon}, default=str),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante l'aggiunta del coupon.", status_code=500)

    else:
        return func.HttpResponse(status_code=404)
