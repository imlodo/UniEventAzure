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
            # tickets = tickets_collection.find({"username": username})
            # 
            # ticket_list = []
            # for ticket in tickets:
            #     ticket_data = {
            #         "ticket_id": ticket.get("ticket_id"),
            #         "event_name": ticket.get("event_name"),
            #         "event_id": ticket.get("t_event_id"),
            #         "status": "Confermato" if ticket.get("status") == "confirmed" else "Annullato",
            #         "creation_date": datetime.strptime(ticket.get("creation_date"), "%Y-%m-%d").strftime("%d/%m/%Y")
            #     }
            #     ticket_list.append(ticket_data)
            
            ticket_list = [
                {
                    "ticket_id": "ABC123",
                    "event_name": "Summer Music Festival",
                    "event_id": "ABCD213SA",
                    "status": "Confermato",
                    "creation_date": "20/06/2023"
                },
                {
                    "ticket_id": "DEF456",
                    "event_name": "Concerto Rock",
                    "status": "Annullato",
                    "event_id": "ABCD213SA",
                    "creation_date": "15/05/2023"
                },
                {
                    "ticket_id": "GHI789",
                    "event_name": "Tech Conference",
                    "status": "Confermato",
                    "event_id": "ABCD213SA",
                    "creation_date": "10/04/2023"
                },
                {
                    "ticket_id": "JKL012",
                    "event_name": "Art Exhibition",
                    "status": "Confermato",
                    "event_id": "ABCD213SA",
                    "creation_date": "25/03/2023"
                },
                {
                    "ticket_id": "MNO345",
                    "event_name": "Food Festival",
                    "status": "Annullato",
                    "event_id": "ABCD213SA",
                    "creation_date": "05/02/2023"
                },
                {
                    "ticket_id": "PQR678",
                    "event_name": "Comedy Night",
                    "status": "Confermato",
                    "event_id": "ABCD213SA",
                    "creation_date": "22/01/2023"
                },
                {
                    "ticket_id": "STU901",
                    "event_name": "Jazz Concert",
                    "status": "Confermato",
                    "event_id": "ABCD213SA",
                    "creation_date": "30/12/2022"
                },
                {
                    "ticket_id": "VWX234",
                    "event_name": "Theater Play",
                    "status": "Annullato",
                    "event_id": "ABCD213SA",
                    "creation_date": "18/11/2022"
                },
                {
                    "ticket_id": "YZA567",
                    "event_name": "Sports Event",
                    "status": "Confermato",
                    "event_id": "ABCD213SA",
                    "creation_date": "14/10/2022"
                },
                {
                    "ticket_id": "BCD890",
                    "event_name": "Dance Performance",
                    "status": "Confermato",
                    "event_id": "ABCD213SA",
                    "creation_date": "29/09/2022"
                },
                {
                    "ticket_id": "EFG123",
                    "event_name": "Film Premiere",
                    "event_id": "ABCD213SA",
                    "status": "Annullato",
                    "creation_date": "12/08/2022"
                },
                {
                    "ticket_id": "HIJ456",
                    "event_name": "Book Fair",
                    "status": "Confermato",
                    "event_id": "ABCD213SA",
                    "creation_date": "04/07/2022"
                },
                {
                    "ticket_id": "KLM789",
                    "event_name": "Science Expo",
                    "status": "Confermato",
                    "event_id": "ABCD213SA",
                    "creation_date": "21/06/2022"
                },
                {
                    "ticket_id": "NOP012",
                    "event_name": "Fashion Show",
                    "status": "Annullato",
                    "event_id": "ABCD213SA",
                    "creation_date": "09/05/2022"
                },
                {
                    "ticket_id": "QRS345",
                    "event_name": "Gaming Convention",
                    "status": "Confermato",
                    "event_id": "ABCD213SA",
                    "creation_date": "31/03/2022"
                }
            ]

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
