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
    logging.info('Add User Address function processed a request.')

    if req.method == 'POST':
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

            t_alias_generated = "JD"  # user.get('t_alias_generated')

            req_body = req.get_json()
            firstName = req_body.get('firstName')
            lastName = req_body.get('lastName')
            street = req_body.get('street')
            city = req_body.get('city')
            state = req_body.get('state')
            zip = req_body.get('zip')

            if not firstName or not lastName or not street or not city or not state or not zip:
                return func.HttpResponse("Indirizzo non valido.", status_code=400)

            user_address = {
                "t_alias_generated": t_alias_generated,
                "firstName": firstName,
                "lastName": lastName,
                "street": street,
                "city": city,
                "state": state,
                "zip": zip
            }

            # user_addresses_collection.insert_one(user_address)

            return func.HttpResponse(json.dumps({"message": "Indirizzo aggiunto con successo."}), status_code=200)

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse("Errore durante l'elaborazione della richiesta.", status_code=500)
    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
