import logging
import os
import json
from pymongo import MongoClient
import azure.functions as func
import jwt

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
content_collection = db.Contents
users_collection = db.Users
content_like_collection = db.ContentLike
content_booked_collection = db.ContentBooked
content_discussion_collection = db.ContentDiscussion

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def get_content_by_current_user(t_alias_generated):
    # Trova tutti i documenti nella collezione dei contenuti con l'alias specificato
    content_list_cursor = content_collection.find({"t_alias_generated": t_alias_generated})

    # Converti il cursore in una lista di dizionari
    content_list = list(content_list_cursor)

    return content_list


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
        try:
            token = req.headers.get('Authorization')
            if not token:
                return func.HttpResponse("Token mancante.", status_code=401)

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

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    "Token non contiene un username valido.",
                    status_code=401
                )

            userRetrived = users_collection.find_one({"t_username": t_username})
            if not userRetrived:
                return func.HttpResponse("Utente non trovato.", status_code=404)

            alias_generated = userRetrived.get("t_alias_generated")
            if not alias_generated:
                return func.HttpResponse("Alias generato non trovato.", status_code=404)

            # Ottieni la lista dei contenuti
            content_list = get_content_by_current_user(alias_generated)

            # Converti ObjectId in stringa se necessario
            for content in content_list:
                if '_id' in content:
                    content['_id'] = str(content['_id'])

            response_body = json.dumps({"content_list": content_list})

            return func.HttpResponse(
                body=response_body,
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero dei contenuti.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo GET.",
            status_code=405
        )
