import logging
import os
import pymongo
import jwt
from azure.functions import HttpResponse
from pymongo import MongoClient
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


def search_users_by_alias_liked(alias_liked):
    users = users_collection.find({"t_alias_generated": {"$regex": alias_liked, "$options": "i"}}).limit(10)
    users_list = []
    for user in users:
        user.pop('_id', None)  # Rimuovi l'ID se presente (per esempio, se è un ObjectId)
        user.pop('t_password', None)  # Rimuovi il campo password se presente (per sicurezza)
        user.pop('t_username', None)
        users_list.append(user)
    return users_list


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Controlla che il metodo della richiesta sia GET
    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            t_alias_generated_liked = req.params.get("t_alias_generated_liked")
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

            # Cerca gli utenti corrispondenti al parametro t_alias_generated_liked
            # if t_alias_generated_liked:
            #     users_info = search_users_by_alias_liked(t_alias_generated_liked)
            # else:
            #     return func.HttpResponse(
            #         status_code=404
            #     )
            
            users_info = [
                {
                    "t_username": "johndoe",
                    "t_name": "John",
                    "t_surname": "Doe",
                    "t_alias_generated": "JD",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR"
                },
                {
                    "t_username": "mariobaldi",
                    "t_name": "Mario",
                    "t_surname": "Baldi",
                    "t_alias_generated": "MarioB",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST"
                },
                {
                    "t_username": "janesmith",
                    "t_name": "Jane",
                    "t_surname": "Smith",
                    "t_alias_generated": "JS",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR"
                },
                {
                    "t_username": "lucabianchi",
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "LB",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST"
                },
                {
                    "t_username": "alicegreen",
                    "t_name": "Alice",
                    "t_surname": "Green",
                    "t_alias_generated": "AGreen",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR"
                },
                {
                    "t_username": "marcobello",
                    "t_name": "Marco",
                    "t_surname": "Bello",
                    "t_alias_generated": "MBello",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST"
                },
                {
                    "t_username": "emilywhite",
                    "t_name": "Emily",
                    "t_surname": "White",
                    "t_alias_generated": "EWhite",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR"
                },
                {
                    "t_username": "giorgioparis",
                    "t_name": "Giorgio",
                    "t_surname": "Paris",
                    "t_alias_generated": "GParis",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST"
                },
                {
                    "t_username": "annagold",
                    "t_name": "Anna",
                    "t_surname": "Gold",
                    "t_alias_generated": "AGold",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR"
                },
                {
                    "t_username": "paolored",
                    "t_name": "Paolo",
                    "t_surname": "Red",
                    "t_alias_generated": "PRed",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST"
                }
            ]

            if users_info:
                # Costruisci il corpo della risposta come oggetto JSON
                response_body = json.dumps({"users": users_info})

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
