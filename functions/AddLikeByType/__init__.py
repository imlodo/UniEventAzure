import json
import logging
import os
from enum import Enum
from random import random

from pymongo import MongoClient
import azure.functions as func
import jwt
from datetime import datetime

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione USERS
users_collection = db.Users

content_like_collection = db.CONTENT_LIKE
discussion_like_collection = db.DISCUSSION_LIKE

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Enum per i ruoli utente
class USER_ROLE(Enum):
    UTENTE = "Utente"
    MODERATORE = "Moderatore"
    SUPERMODERATORE = "Super Moderatore"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Ottieni il token JWT dall'header Authorization
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

        # Recupera l'utente dal database usando t_username
        # user = users_collection.find_one({"t_username": t_username})
        # if not user:
        #     return func.HttpResponse(
        #         "Utente non trovato.",
        #         status_code=404
        #     )

        req_body = req.get_json()
        t_alias_generated = req_body.get('t_alias_generated')
        content_id = req_body.get('content_id')
        discussion_id = req_body.get('discussion_id')
        like_type = req_body.get('like_type')

        if not t_alias_generated:
            return func.HttpResponse(
                "Il parametro t_alias_generated è obbligatorio.",
                status_code=400
            )

        # Recupera l'utente dal t_alias_generated
        # user = users_collection.find_one({"t_alias_generated": t_alias_generated})

        # if not user:
        #     return func.HttpResponse(
        #         "Utente non trovato.",
        #         status_code=404
        #     )

        t_username = "baldi"  # user.get('username')

        if like_type == "LIKE_CONTENT":
            if not content_id:
                return func.HttpResponse(
                    "Il parametro content_id è obbligatorio.",
                    status_code=400
                )
            # existing_record = content_like_collection.find_one({"content_id": content_id, "t_username": t_username})
            # if existing_record:
            #     content_like_collection.delete_one({"content_id": content_id, "t_username": t_username})
            #     return func.HttpResponse(
            #         body=json.dumps({"liked": False,"message": "Contenuto rimosso dai piaciuti"}),
            #         status_code=201,
            #         mimetype='application/json'
            #     )
            # # Crea un nuovo record nella tabella CONTENT_BOOKED
            # new_record = {
            #     "content_id": content_id,
            #     "t_username": t_username,
            #     "created_at": datetime.utcnow()
            # }
            # 
            # content_like_collection.insert_one(new_record)
            # return func.HttpResponse(
            #     body=json.dumps({"liked": True, "message": "Contenuto aggiunto ai piaciuti"}),
            #     status_code=201,
            #     mimetype='application/json'
            # )
            if random() > 0.5:
                return func.HttpResponse(
                    body=json.dumps({"liked": True, "message": "Contenuto aggiunto ai piaciuti"}),
                    status_code=201,
                    mimetype='application/json'
                )
            return func.HttpResponse(
                body=json.dumps({"liked": False, "message": "Contenuto rimosso dai piaciuti"}),
                status_code=201,
                mimetype='application/json'
            )

        elif like_type == "LIKE_DISCUSSION":
            if not discussion_id or not content_id:
                return func.HttpResponse(
                    "I parametri discussion_id e content_id sono obbligatori.",
                    status_code=400
                )
            # existing_record = discussion_like_collection.find_one({"content_id": content_id, "discussion_id": discussion_id, "t_username": t_username})
            # if existing_record:
            #     discussion_like_collection.delete_one({"discussion_id": discussion_id, "t_username": t_username})
            #     return func.HttpResponse(
            #         body=json.dumps({"liked": False,"message": "Commento rimosso dai piaciuti"}),
            #         status_code=201,
            #         mimetype='application/json'
            #     )
            # # Crea un nuovo record nella tabella CONTENT_BOOKED
            # new_record = {
            #     "content_id": content_id,
            #     "discussion_id": discussion_id,
            #     "t_username": t_username,
            #     "created_at": datetime.utcnow()
            # }
            # 
            # discussion_like_collection.insert_one(new_record)
            # return func.HttpResponse(
            #     body=json.dumps({"liked": True, "message": "Commento aggiunto ai piaciuti"}),
            #     status_code=201,
            #     mimetype='application/json'
            # )
            if random() > 0.5:
                return func.HttpResponse(
                    body=json.dumps({"liked": True, "message": "Commento aggiunto ai piaciuti"}),
                    status_code=201,
                    mimetype='application/json'
                )
            return func.HttpResponse(
                body=json.dumps({"liked": False, "message": "Commento rimosso dai piaciuti"}),
                status_code=201,
                mimetype='application/json'
            )

        else:
            return func.HttpResponse(
                "Il tipo di like è errato.",
                status_code=400
            )

    except ValueError as ve:
        logging.error(f"Errore: {ve}")
        return func.HttpResponse(
            str(ve),
            status_code=400
        )
    except Exception as e:
        logging.error(f"Errore: {e}")
        return func.HttpResponse(
            "Errore durante l'elaborazione della richiesta.",
            status_code=500
        )
