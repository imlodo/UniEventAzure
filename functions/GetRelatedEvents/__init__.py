import logging
import os
import json
from datetime import datetime

import jwt
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
import azure.functions as func

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Ottieni la stringa di connessione dal file delle variabili d'ambiente
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def serialize_document(doc):
    """Converte ObjectId e altri tipi non serializzabili in stringhe."""
    if isinstance(doc, list):
        return [serialize_document(item) for item in doc]
    elif isinstance(doc, dict):
        return {key: serialize_document(value) for key, value in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
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
                return func.HttpResponse("Token scaduto.", status_code=401)
            except jwt.InvalidTokenError:
                return func.HttpResponse("Token non valido.", status_code=401)

            # Ottieni l'username dal token decodificato
            username = decoded_token.get('username')
            if not username:
                return func.HttpResponse("Token non contiene un username valido.", status_code=401)

            # Ottieni il parametro n_group_id dalla query string
            n_group_id = req.params.get('n_group_id')
            if not n_group_id:
                return func.HttpResponse("n_group_id è richiesto.", status_code=400)

            # Recupera gli eventi dal database
            events = db.Contents.find({"n_group_id": int(n_group_id)})

            event_details = []
            for eventEl in events:
                event_id = eventEl.get("_id")
                t_alias_generated = eventEl.get("t_alias_generated")

                # Recupera l'utente
                user = db.Users.find_one({"t_alias_generated": t_alias_generated})

                # Recupera le mappe
                maps = list(db.EventMaps.find({"t_map_event_id": ObjectId(event_id)}))
                for map_item in maps:
                    t_map_id = map_item.get("_id")

                    # Recupera gli oggetti della mappa
                    object_maps = list(db.ObjectMaps.find({"n_id_map": t_map_id}))
                    map_item["t_object_maps"] = object_maps

                # Recupera le recensioni
                reviews = list(db.TicketReviews.find({"t_event_id": ObjectId(event_id)}))
                reviews_list = []
                for review in reviews:
                    reviewEdit = review
                    reviewEdit["t_user"]={
                        #mock per velocizzare
                        t_alias_generated: eventEl.get("t_alias_generated")
                    }
                    reviews_list.append(reviewEdit)
                # Recupera la location
                location = db.EventLocation.find_one({"event_id": ObjectId(event_id)})

                # Costruisci l'oggetto EventDetail
                event_detail = {
                    "id": str(event_id),
                    "n_group_id": eventEl.get("n_group_id"),
                    "n_click": eventEl.get("n_click"),
                    "t_caption": eventEl.get("t_caption"),
                    "t_image_link": eventEl.get("t_image_link"),
                    "t_event_date": eventEl.get("t_event_date"),
                    "t_map_list": serialize_document(maps),
                    "t_reviews": serialize_document(reviews_list),
                    "t_user": serialize_document(user),
                    "t_location": serialize_document(location),
                    "b_active": eventEl.get("b_active"),
                    "t_privacy": eventEl.get("t_privacy")
                }

                event_details.append(event_detail)

            return func.HttpResponse(
                body=json.dumps(event_details),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero dei dettagli degli eventi.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo GET.",
            status_code=405
        )
