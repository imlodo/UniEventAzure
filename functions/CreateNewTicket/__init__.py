import logging
import os
import json
from datetime import datetime, timedelta
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
users_collection = db.Users  # Supponiamo che ci sia una collezione Users per ottenere alias e ruolo

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

# Ruoli permessi
ALLOWED_ROLES = {"Utente", "Moderatore", "Super Moderatore"}


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

            #Recupera l'alias e il ruolo dal database usando l'username
            user_data = users_collection.find_one({"username": username})
            if not user_data:
                return func.HttpResponse("Utente non trovato.", status_code=404)

            alias = user_data.get("alias")
            role = user_data.get("role")

            if not alias or not role:
                return func.HttpResponse("Dati dell'utente mancanti.", status_code=400)

            # Controlla se il ruolo è valido
            if role not in ALLOWED_ROLES:
                return func.HttpResponse("Ruolo dell'utente non valido.", status_code=400)

            # Ottieni i dati dalla richiesta
            try:
                req_body = req.get_json()
                description = req_body.get('description')
                attachments = req_body.get('attachments', [])
            except ValueError:
                return func.HttpResponse("Richiesta non valida.", status_code=400)

            # Controlla se i campi obbligatori sono presenti
            if not description:
                return func.HttpResponse("Descrizione mancante per il ticket.", status_code=400)

            # Calcola la data di scadenza
            expired_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

            # Crea un nuovo ticket di supporto
            ticket = {
                "t_username": username,
                "description": description,
                "status": "Aperto",
                "expired_date": expired_date,
                "isScaduto": False
            }

            # Inserisce il ticket nel database
            ticketRes = support_tickets_collection.insert_one(ticket)

            # Crea il primo messaggio della discussione del ticket di supporto
            discussion = {
                "support_ticket_id": ticketRes["_id"],
                "alias": alias,
                "role": role,
                "replyDateHour": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "body": description,
                "attachments": attachments
            }

            # Inserisce la discussione nel database
            support_ticket_discussion_collection.insert_one(discussion)

            response_body = json.dumps({"message": "Ticket di supporto creato con successo."})
            return func.HttpResponse(
                body=response_body,
                status_code=201,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante la creazione del ticket di supporto.",
                                     status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
