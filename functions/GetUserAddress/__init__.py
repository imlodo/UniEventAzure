import logging
import os
from datetime import datetime, timedelta
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
user_addresses_collection = db.UserAddresses
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

# Funzione per decodificare il token JWT e ottenere l'username
def get_username_from_token(token):
    secret_key = os.getenv('JWT_SECRET_KEY')
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded_token.get('username')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get User Addresses function processed a request.')

    if req.method == 'GET':
        try:
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse("Autorizzazione non valida.", status_code=401)

            jwt_token = auth_header.split(' ')[1]
            t_username = get_username_from_token(jwt_token)
            if not t_username:
                return func.HttpResponse("Token non valido.", status_code=401)

            # user = users_collection.find_one({"t_username": t_username})
            # if not user:
            #     return func.HttpResponse("Utente non trovato.", status_code=404)
            # 
            # t_alias_generated = user.get('t_alias_generated')
            # 
            # user_addresses = list(user_addresses_collection.find({"t_alias_generated": t_alias_generated}))
            user_addresses = [
                {
                    "address_id": "asjhaskkasjd38y273",
                    "firstName": "John",
                    "lastName": "Doe",
                    "street": "123 Main St",
                    "city": "Springfield",
                    "state": "IL",
                    "zip": 62701
                },
                {
                    "address_id": "asdjasjdjasjdah312",
                    "firstName": "Jane",
                    "lastName": "Doe",
                    "street": "456 Elm St",
                    "city": "Springfield",
                    "state": "IL",
                    "zip": 62702
                }
            ]
            
            return func.HttpResponse(
                body=json.dumps(user_addresses),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse("Errore durante l'elaborazione della richiesta.", status_code=500)
    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo GET.", status_code=405)
