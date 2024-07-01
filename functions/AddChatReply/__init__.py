import logging
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import azure.functions as func
import jwt

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Ottieni la stringa di connessione dal file delle variabili d'ambiente
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
users_collection = db.Users
messages_collection = db.Messages

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

# Funzione principale dell'Azure Function
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

            # Ottieni i dati dalla richiesta
            try:
                req_body = req.get_json()
                alias_generated = req_body.get('t_alias_generated')
                message = req_body.get('message')
            except ValueError:
                return func.HttpResponse("Richiesta non valida.", status_code=400)

            # Controlla se i campi obbligatori sono presenti
            if not all([alias_generated, message]):
                return func.HttpResponse("Dati mancanti per il messaggio.", status_code=400)

            # Recupera l'utente di destinazione dal database tramite l'alias generato
            # user_at = users_collection.find_one({"t_alias_generated": alias_generated})
            # if not user_at:
            #     return func.HttpResponse("Utente destinatario non trovato.", status_code=404)

            # Prepara il nuovo messaggio
            new_message = {
                "user_from": username,
                "user_at": "", #user_at['t_username'],
                "message": message,
                "dateTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }

            # Inserisce il nuovo messaggio nel database
            #messages_collection.insert_one(new_message)

            response_body = json.dumps({"message": "Messaggio inviato con successo."})
            return func.HttpResponse(
                body=response_body,
                status_code=201,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante l'invio del messaggio.", status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
