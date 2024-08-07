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
user_cards_collection = db.UserCards
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
    logging.info('Add User Card function processed a request.')

    if req.method == 'POST':
        try:
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse("Autorizzazione non valida.", status_code=401)

            jwt_token = auth_header.split(' ')[1]
            t_username = get_username_from_token(jwt_token)
            if not t_username:
                return func.HttpResponse("Token non valido.", status_code=401)

            user = users_collection.find_one({"t_username": t_username})
            if not user:
                return func.HttpResponse("Utente non trovato.", status_code=404)

            t_alias_generated = user.get('t_alias_generated')

            req_body = req.get_json()
            cardName = req_body.get('cardName')
            cardNumber = req_body.get('cardNumber')
            expiryDate = req_body.get('expiryDate')
            cvv = req_body.get('cvv')
            
            if not cardName or not cardNumber or not expiryDate or not cvv or len(cvv) > 3:
                return func.HttpResponse("Carta non valida.", status_code=400)
            
            user_card = {
                "t_alias_generated": t_alias_generated,
                "cardName": cardName,
                "cardNumber": cardNumber,
                "expiryDate": expiryDate,
                "cvv": cvv
            }

            user_cards_collection.insert_one(user_card)

            return func.HttpResponse(json.dumps({"message":"Carta aggiunta con successo."}), status_code=200)

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse("Errore durante l'elaborazione della richiesta.", status_code=500)
    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
