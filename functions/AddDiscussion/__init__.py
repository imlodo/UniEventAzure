import json
import logging
import os
from datetime import datetime

import azure.functions as func
import jwt
from pymongo import MongoClient

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
users_collection = db.Users
discussion_collection = db.ContentDiscussion

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    if req.method == 'POST':
        try:
            # Ottieni il token JWT dall'header Authorization
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

            # Ottieni l'username dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse("Token non contiene un username valido.", status_code=401)

            try:
                req_body = req.get_json()
                content_id = req_body.get('content_id')
                if not content_id:
                    return func.HttpResponse(
                        "Il parametro content_id è obbligatorio.",
                        status_code=400
                    )
                parent_discussion_id = req_body.get('parent_discussion_id')
                t_alias_generated_reply = req_body.get('t_alias_generated_reply')
                body = req_body.get('body')
                if not body:
                    return func.HttpResponse(
                        "Il parametro body è obbligatorio.",
                        status_code=400
                    )
                # t_user = users_collection.find_one({"t_username": t_username})
                t_user = {
                    "id": 1,
                    "t_name": "Mario Rossi",
                    "t_follower_number": 1000,
                    "t_alias_generated": "mariorossi",
                    "t_description": "Appassionato di tecnologia e innovazione.",
                    "t_profile_photo": "/assets/img/example_artist_image.jpg",
                    "t_type": 1,
                    "is_verified": True,
                    "type": "Utenti"
                }
                if not t_user:
                    return func.HttpResponse(
                        "Utente non valido",
                        status_code=400
                    )
                created_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

                # new_discussion = {
                #     "content_id": content_id,
                #     "parent_discussion_id": parent_discussion_id,
                #     "body": body,
                #     "like_count": 0,
                #     "t_user": t_user,
                #     "created_date": created_date,
                #     "is_liked_by_current_user": False,
                #     "t_alias_generated_reply": t_alias_generated_reply
                # }
                # 
                # result = discussion_collection.insert_one(new_discussion)
                # inserted_discussion = discussion_collection.find_one({"_id": result.inserted_id})

                inserted_discussion = {
                    "content_id": content_id,
                    "discussion_id": "ABCD123",
                    "parent_discussion_id": parent_discussion_id,
                    "body": body,
                    "like_count": 0,
                    "t_user": t_user,
                    "created_date": created_date,
                    "t_alias_generated_reply": t_alias_generated_reply
                }
                return func.HttpResponse(
                    json.dumps({"discussion": inserted_discussion}, default=str),
                    status_code=200,
                    mimetype='application/json'
                )

            except ValueError:
                return func.HttpResponse("Richiesta non valida.", status_code=400)

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse(
                "Errore durante l'elaborazione della richiesta.",
                status_code=500
            )
    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
