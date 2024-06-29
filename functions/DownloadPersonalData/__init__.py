import logging
import os
from random import random

import jwt
import json
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

# Seleziona la collezione per le richieste di download dei dati personali
requests_collection = db.PERSONAL_DATA_REQUESTS

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
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
            username = decoded_token.get('username')
            if not username:
                return func.HttpResponse("Token non contiene un username valido.", status_code=401)

            # Recupera la richiesta dal database
            #request_data = requests_collection.find_one(
            #    {"t_username": username},
            #    {"_id": 0, "status": 1, "download_file": 1, "type_data_download": 1}
            #)
            #if not request_data or request_data.get("status") != "DOWNLODABLE":
            if random() > 0.5:
                return func.HttpResponse("Il file non è pronto per il download.", status_code=404)

            #download_file = request_data.get("download_file")
            #type_data_download = request_data.get("type_data_download")

            download_file = {
                "chat_data": {
                    "conversations": [
                        {
                            "with": "user123",
                            "messages": [
                                {
                                    "timestamp": "2023-06-20T10:30:00Z",
                                    "message": "Ciao, come stai?"
                                },
                                {
                                    "timestamp": "2023-06-20T10:32:00Z",
                                    "message": "Sto bene, grazie! E tu?"
                                }
                            ]
                        },
                        {
                            "with": "user456",
                            "messages": [
                                {
                                    "timestamp": "2023-06-21T14:15:00Z",
                                    "message": "Hai visto l'ultimo film?"
                                },
                                {
                                    "timestamp": "2023-06-21T14:17:00Z",
                                    "message": "Sì, è stato fantastico!"
                                }
                            ]
                        }
                    ]
                },
                "content_data": {
                    "posts": [
                        {
                            "post_id": "post123",
                            "content": "Ecco una nuova foto del mio viaggio!",
                            "timestamp": "2023-06-18T09:00:00Z"
                        },
                        {
                            "post_id": "post124",
                            "content": "Buon compleanno a me!",
                            "timestamp": "2023-06-19T10:00:00Z"
                        }
                    ],
                    "likes": [
                        {
                            "post_id": "post125",
                            "timestamp": "2023-06-20T12:00:00Z"
                        },
                        {
                            "post_id": "post126",
                            "timestamp": "2023-06-21T08:00:00Z"
                        }
                    ]
                },
                "booked_data": {
                    "events": [
                        {
                            "event_id": "event123",
                            "name": "Concerto di musica",
                            "date": "2023-07-01T20:00:00Z"
                        },
                        {
                            "event_id": "event124",
                            "name": "Conferenza di tecnologia",
                            "date": "2023-07-05T09:00:00Z"
                        }
                    ]
                },
                "interaction_data": {
                    "followers": [
                        {
                            "username": "user789",
                            "followed_on": "2023-06-15T08:30:00Z"
                        },
                        {
                            "username": "user101",
                            "followed_on": "2023-06-16T10:00:00Z"
                        }
                    ],
                    "following": [
                        {
                            "username": "user234",
                            "followed_on": "2023-06-17T11:30:00Z"
                        },
                        {
                            "username": "user567",
                            "followed_on": "2023-06-18T14:00:00Z"
                        }
                    ]
                }
            }

            type_data_download = "TXT" if random() > 0.5 else "JSON"

            if not download_file:
                return func.HttpResponse("Il file non è disponibile.", status_code=404)

            response_body = json.dumps({
                "download_file": download_file,
                "type_data_download": type_data_download
            })
            return func.HttpResponse(body=response_body, status_code=200, mimetype='application/json')

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante il download dei dati personali.",
                                     status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo GET.", status_code=405)
