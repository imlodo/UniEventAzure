import logging
import os
from datetime import datetime
import jwt
import json

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

# Seleziona la collezione dei biglietti
tickets_collection = db.Tickets
content_collection = db.Contents

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

            # Ottieni il numero del biglietto dalla query string
            ticket_id = req.params.get('ticket_id')
            if not ticket_id:
                return func.HttpResponse("Numero del biglietto non fornito.", status_code=400)

            # Recupera il biglietto dal database
            ticket = tickets_collection.find_one({"t_username": username, "_id": ObjectId(ticket_id)})
            if not ticket:
                return func.HttpResponse("Biglietto non trovato.", status_code=404)

            # Gestione della data e ora
            try:
                creation_date = datetime.strptime(ticket.get("creation_date"), "%Y-%m-%dT%H:%M:%S.%f")
                formatted_creation_date = creation_date.strftime("%d/%m/%Y %H:%M:%S")
            except ValueError:
                # Se il formato della data è diverso, gestisci l'errore o usa un formato alternativo
                formatted_creation_date = ticket.get("creation_date")  # Usa il valore originale se non riesci a parsarlo

            eventDetail = content_collection.find_one({"_id": ObjectId(ticket.get("event_id"))})
            # Converti ObjectId in stringa
            ticket_detail = {
                "ticket_id": str(ticket.get("_id")),  # Assicurati che ticket_id sia in formato stringa
                "status": "Confermato" if ticket.get("status") == "Confermato" or ticket.get("status") == "confirmed" else "Annullato",
                "creation_date": formatted_creation_date,
                "ticket_type": ticket.get("ticket_type", {}),
                "price": "{:.2f}".format(ticket.get("price", 0)),
                "event": {
                    "event_id": str(ticket.get("event_id")),  # Assicurati che event_id sia in formato stringa
                    "t_title": eventDetail.get("t_caption"),
                    "t_event_date": eventDetail.get("t_event_date"),
                    "t_image_link": eventDetail.get("t_image_link")
                }
            }

            return func.HttpResponse(
                body=json.dumps(ticket_detail),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante il recupero del dettaglio del biglietto.", status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo GET.", status_code=405)
