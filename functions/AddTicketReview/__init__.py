import logging
import os
import json
from datetime import datetime
from random import random

from bson import ObjectId
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

# Seleziona la collezione per le recensioni dei biglietti
reviews_collection = db.TicketReviews

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
                ticket_id = req_body.get('t_ticket_id')
                event_id = req_body.get("t_event_id")
                title = req_body.get('t_title')
                body = req_body.get('t_body')
                star = req_body.get('n_star')
                review_date = req_body.get('review_date')
            except ValueError:
                return func.HttpResponse("Richiesta non valida.", status_code=400)

            # Controlla se i campi obbligatori sono presenti
            if not all([ticket_id, event_id, title, body, star, review_date]):
                return func.HttpResponse("Dati mancanti per la recensione.", status_code=400)

            # Controlla se il numero di stelle è nel range corretto
            if not (0.5 <= star <= 5):
                return func.HttpResponse("Il numero di stelle deve essere tra 0.5 e 5.", status_code=400)

            # Crea un nuovo record per la recensione o aggiorna l'esistente
            review = {
                "t_username": username,
                "t_ticket_id": ObjectId(ticket_id),
                "t_event_id": ObjectId(event_id),
                "t_title": title,
                "t_body": body,
                "n_star": star,
                "review_date": review_date,
                "created_date": datetime.utcnow().strftime("%Y-%m-%d")
            }

            # Cerca se esiste già una recensione per l'utente e il biglietto
            existing_review = reviews_collection.find_one({"t_username": username, "t_ticket_id": ObjectId(ticket_id)})

            if existing_review:
                # Aggiorna la recensione esistente
                reviews_collection.update_one(
                    {"t_username": username, "t_ticket_id": ObjectId(ticket_id)},
                    {"$set": review}
                )
                response_message = "Recensione aggiornata con successo."
            else:
                # Inserisce una nuova recensione
                reviews_collection.insert_one(review)
                response_message = "Recensione aggiunta con successo."

            response_body = json.dumps({"message": response_message})
            return func.HttpResponse(
                body=response_body,
                status_code=201,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante l'aggiunta o l'aggiornamento della recensione.", status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
