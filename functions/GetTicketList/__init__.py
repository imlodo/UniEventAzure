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

# Seleziona la collezione dei biglietti
tickets_collection = db.Tickets
content_collection = db.Contents
# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

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

            # Recupera i biglietti dal database
            tickets = tickets_collection.find({"t_username": username})

            ticket_list = []
            for ticket in tickets:
                # Converti la stringa della data e ora nel formato corretto
                creation_date_str = ticket.get("creation_date")
                if creation_date_str:
                    try:
                        parsed_date = datetime.strptime(creation_date_str, "%Y-%m-%dT%H:%M:%S.%f")
                        formatted_date = parsed_date.strftime("%d/%m/%Y")
                    except ValueError:
                        # Gestisci il caso di errore se la stringa della data non è nel formato previsto
                        formatted_date = creation_date_str
                else:
                    formatted_date = "Data non disponibile"
                
                event_name = content_collection.find_one({"_id":ticket.get("event_id")}).get("t_caption")
                ticket_data = {
                    "ticket_id": str(ticket.get("_id")),
                    "event_name": event_name,
                    "event_id": str(ticket.get("event_id")),
                    "status": "Confermato" if ticket.get("status") == "Confermato" or ticket.get("status") == "confirmed" else "Annullato",
                    "creation_date": formatted_date
                }
                ticket_list.append(ticket_data)

            return func.HttpResponse(
                body=json.dumps(ticket_list),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero della lista dei biglietti.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo GET.",
            status_code=405
        )
