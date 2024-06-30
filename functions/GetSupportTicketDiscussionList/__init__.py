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

# Seleziona le collezioni per i ticket di supporto e le discussioni
support_tickets_collection = db.SupportTickets
support_ticket_discussion_collection = db.SupportTicketDiscussion

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

            # Ottieni il ticket_id dal percorso della richiesta
            ticket_id = req.params.get('ticket_id')
            if not ticket_id:
                return func.HttpResponse("Ticket ID mancante nella richiesta.", status_code=400)

            # Verifica se l'utente è associato al ticket
            # ticket = support_tickets_collection.find_one({"id": ticket_id, "t_username": username})
            # if not ticket:
            #     return func.HttpResponse("Utente non autorizzato a visualizzare questo ticket.", status_code=403)

            # Recupera tutte le risposte per il ticket
            #discussions = list(support_ticket_discussion_collection.find({"support_ticket_id": ticket_id}))

            # Trasforma il risultato in una lista di dizionari
            discussion_list = []
            # for discussion in discussions:
            #     discussion_list.append({
            #         "support_ticket_id": discussion.get("support_ticket_id"),
            #         "alias": discussion.get("alias"),
            #         "role": discussion.get("role"),
            #         "replyDateHour": discussion.get("replyDateHour"),
            #         "body": discussion.get("body"),
            #         "attachments": discussion.get("attachments", [])
            #     })

            discussion_list = [
                {
                    "support_ticket_id": "ticket123",
                    "alias": "JD",
                    "role": "Utente",
                    "replyDateHour": "20/06/2024 10:30",
                    "body": "Descrizione del problema 1",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                },
                {
                    "support_ticket_id": "ticket123",
                    "alias": "user_alias2",
                    "role": "Moderatore",
                    "replyDateHour": "21/06/2024 11:00",
                    "body": "Descrizione del problema 2",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                },
                {
                    "support_ticket_id": "ticket123",
                    "alias": "user_alias3",
                    "role": "Super Moderatore",
                    "replyDateHour": "22/06/2024 12:15",
                    "body": "Descrizione del problema 3",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                },
                {
                    "support_ticket_id": "ticket123",
                    "alias": "user_alias4",
                    "role": "Moderatore",
                    "replyDateHour": "23/06/2024 13:45",
                    "body": "Descrizione del problema 4",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                },
                {
                    "support_ticket_id": "ticket123",
                    "alias": "user_alias5",
                    "role": "Moderatore",
                    "replyDateHour": "24/06/2024 14:30",
                    "body": "Descrizione del problema 5",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                },
                {
                    "support_ticket_id": "ticket123",
                    "alias": "user_alias6",
                    "role": "Moderatore",
                    "replyDateHour": "25/06/2024 15:00",
                    "body": "Descrizione del problema 6",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                },
                {
                    "support_ticket_id": "ticket123",
                    "alias": "user_alias7",
                    "role": "Moderatore",
                    "replyDateHour": "26/06/2024 16:30",
                    "body": "Descrizione del problema 7",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                },
                {
                    "support_ticket_id": "ticket123",
                    "alias": "user_alias8",
                    "role": "Moderatore",
                    "replyDateHour": "27/06/2024 17:45",
                    "body": "Descrizione del problema 8",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                },
                {
                    "support_ticket_id": "ticket123",
                    "alias": "user_alias9",
                    "role": "Moderatore",
                    "replyDateHour": "28/06/2024 18:00",
                    "body": "Descrizione del problema 9",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                },
                {
                    "support_ticket_id": "ticket123",
                    "alias": "user_alias10",
                    "role": "Moderatore",
                    "replyDateHour": "29/06/2024 19:15",
                    "body": "Descrizione del problema 10",
                    "attachments": ["http://localhost:4200/assets/img/example_artist_image.jpg"]
                }
            ]
            
            response_body = json.dumps(discussion_list)
            return func.HttpResponse(body=response_body, status_code=200, mimetype='application/json')

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante il recupero dei dettagli del ticket.", status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo GET.", status_code=405)
