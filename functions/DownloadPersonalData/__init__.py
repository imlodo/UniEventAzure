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
requests_collection = db.RequestPersonalData

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
            request_data = requests_collection.find_one(
               {"t_username": username},
               {"_id": 0, "status": 1, "download_file": 1, "type_data_download": 1}
            )
            if not request_data or request_data.get("status") != "DOWNLODABLE":
                return func.HttpResponse("Il file non è pronto per il download.", status_code=404)

            download_file = request_data.get("download_file")
            type_data_download = request_data.get("type_data_download")

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
