import logging
import os
import pymongo
import jwt
from azure.functions import HttpResponse
from pymongo import MongoClient
from datetime import datetime, timedelta
import azure.functions as func
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def get_user_info_by_username(t_username):
    user = users_collection.find_one({"t_username": t_username})
    if user:
        # Rimuovi l'ID se presente (per esempio, se è un ObjectId)
        if '_id' in user:
            del user['_id']
        # Rimuovi il campo password se presente (per sicurezza)
        if 't_password' in user:
            del user['t_password']
        return user
    return None


def get_user_info_by_alias(alias):
    user = users_collection.find_one({"t_alias_generated": alias})
    if user:
        # Rimuovi l'ID se presente (per esempio, se è un ObjectId)
        if '_id' in user:
            del user['_id']
        # Rimuovi il campo password se presente (per sicurezza)
        if 't_password' in user:
            del user['t_password']
        return user
    return None


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Controlla che il metodo della richiesta sia GET
    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            alias_generated = req.params.get("t_alias_generated")
            if alias_generated:
                print(alias_generated)
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    status_code=404
                )

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')

            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    status_code=404
                )
            except jwt.InvalidTokenError:
                return func.HttpResponse(
                    status_code=404
                )

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    status_code=404
                )

            # Ottieni le informazioni complete dell'utente dal database
            if alias_generated:
                # user_info = get_user_info_by_alias(alias_generated)
                if alias_generated == "JD":
                    user_info = dict(_id="012933923", t_username="johndoe", t_password="hashed_password", t_name="John",
                                     t_surname="Doe",
                                     t_alias_generated="JD", t_description="Lorem ipsum dolor sit amet.",
                                     t_profile_photo="http://localhost:4200/assets/img/userExampleImg.jpeg",
                                     is_verified=False,
                                     t_type="COMPANY",
                                     t_role="Moderatore")
                else:
                    user_info = dict(_id="012933924", t_username="mariobaldi", t_password="hashed_password",
                                     t_name="Mario",
                                     t_surname="Baldi",
                                     t_alias_generated="Mario Baldi", t_description="Lorem ipsum dolor sit amet.",
                                     t_profile_photo="http://localhost:4200/assets/img/dolcevita.png",
                                     is_verified=True,
                                     t_type="COMPANY",
                                     t_role="Moderatore") #"Super Moderatore" "Utente"
            else:
                # user_info = get_user_info_by_username(t_username)
                user_info = dict(_id="012933923", t_username="johndoe", t_password="hashed_password", t_name="John",
                                 t_surname="Doe",
                                 t_alias_generated="JD", t_description="Lorem ipsum dolor sit amet.",
                                 t_profile_photo="http://localhost:4200/assets/img/userExampleImg.jpeg",
                                 is_verified=False,
                                 t_type="COMPANY",
                                 t_role="Moderatore")

            if user_info:
                # Costruisci il corpo della risposta come oggetto JSON senza 't_password' e '_id'
                user_response = {"user": user_info}
                response_body = json.dumps(user_response)

                return func.HttpResponse(
                    body=response_body,
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    status_code=404
                )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero delle informazioni utente.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            status_code=404
        )
