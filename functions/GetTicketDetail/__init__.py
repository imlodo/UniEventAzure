import logging
import os
from datetime import datetime
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

# Seleziona la collezione dei biglietti
tickets_collection = db.TICKETS

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
            #ticket = tickets_collection.find_one({"username": username, "ticket_id": ticket_id})
            #if not ticket:
                #return func.HttpResponse("Biglietto non trovato.", status_code=404)
            
            ticket_detail = {
                "ticket_id": "ABC123",
                "status": "Confermato",
                "creation_date": "20/06/2023",
                "ticket_type": {
                    "TABLE": {
                        "DISCOTECA": True,
                        "DISCOTECA_DJ": False
                    }
                },
                "price": "50.00",
                "event": {
                    "t_title": "Summer Music Festival",
                    "t_event_date": "15/07/2023",
                    "t_image_link": "/assets/img/event-image-placeholder.jpg"
                }
            }
            # ticket_detail = {
            #     "ticket_id": ticket.get("ticket_id"),
            #     "status": "Confermato" if ticket.get("status") == "confirmed" else "Annullato",
            #     "creation_date": datetime.strptime(ticket.get("creation_date"), "%Y-%m-%d").strftime("%d/%m/%Y"),
            #     "ticket_type": ticket.get("ticket_type", {}),
            #     "price": "{:.2f}".format(ticket.get("price", 0)),
            #     "event": {
            #         "t_title": ticket.get("event_name"),
            #         "t_event_date": ticket.get("event_date"),
            #         "t_image_link": ticket.get("event_image_link")
            #     }
            # }

            return func.HttpResponse(
                body=json.dumps(ticket_detail),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante il recupero del dettaglio del biglietto.",
                                     status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo GET.", status_code=405)
