import logging
import os
import json
from datetime import datetime
import jwt
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
requests_collection = db.PersonalDataRequest
user_data_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def create_personal_data_file(t_username, type_download, type_data_download):
    # Recupera i dati dell'utente
    user_data = user_data_collection.find_one({"t_username": t_username}, {"_id": 0})
    if not user_data:
        raise ValueError("Nessun dato trovato per l'utente.")

    # Filtra i dati in base a type_download, va modificata
    filtered_data = {}
    if type_download == "ALL_DATA" or "CHAT_DATA" in type_download:
        filtered_data["chat_data"] = user_data.get("chat_data", {})
    if type_download == "ALL_DATA" or "CONTENT_DATA" in type_download:
        filtered_data["content_data"] = user_data.get("content_data", {})
    if type_download == "ALL_DATA" or "BOOKED_DATA" in type_download:
        filtered_data["booked_data"] = user_data.get("booked_data", {})
    if type_download == "ALL_DATA" or "INTERACTION_DATA" in type_download:
        filtered_data["interaction_data"] = user_data.get("interaction_data", {})

    # Converti i dati nel formato richiesto
    if type_data_download == "JSON":
        download_file = json.dumps(filtered_data)
    elif type_data_download == "TXT":
        download_file = ""
        for key, value in filtered_data.items():
            download_file += f"{key}:\n{json.dumps(value, indent=2)}\n\n"

    # Aggiorna la richiesta nel database
    requests_collection.update_one(
        {"t_username": t_username, "status": "REQUESTED"},
        {"$set": {"status": "DOWNLODABLE", "download_file": download_file}}
    )


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
            username = decoded_token.get('username')
            if not username:
                return func.HttpResponse("Token non contiene un username valido.", status_code=401)

            # Prova a ottenere i dati JSON dal corpo della richiesta
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse("La richiesta non contiene dati JSON validi.", status_code=400)

            # Estrai i parametri dal corpo della richiesta
            type_download = req_body.get('type_download')
            type_data_download = req_body.get('type_data_download')
            if not type_download or not type_data_download:
                return func.HttpResponse("Inserire type_download e type_data_download nel corpo della richiesta.",
                                         status_code=400)

            # Crea la richiesta nel database
            request_data = {
                "t_username": username,
                "type_download": type_download,
                "type_data_download": type_data_download,
                "status": "REQUESTED",
                "timestamp": datetime.utcnow()
            }
            #requests_collection.insert_one(request_data)

            # Invoca la funzione per creare il file di dati personali
            #create_personal_data_file(username, type_download, type_data_download)

            response_body = json.dumps({"message": "Richiesta di dati personali inviata con successo."})
            return func.HttpResponse(body=response_body, status_code=200, mimetype='application/json')

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante la richiesta di dati personali.",
                                     status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
