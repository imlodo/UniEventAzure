import logging
import os
import json
from datetime import datetime, timedelta

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
users_collection = db.Users  # Supponiamo che ci sia una collezione Users per ottenere alias e ruolo
ALLOWED_ROLES = {"Utente", "Moderatore", "Super Moderatore"}

# Seleziona le collezioni per i ticket di supporto e le discussioni
support_ticket_collection = db.SupportTickets
support_ticket_discussion_collection = db.SupportTicketDiscussion

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

            # Ottieni l'username, alias e role dal token decodificato
            username = decoded_token.get('username')
            if not username:
                return func.HttpResponse("Token non contiene informazioni valide.", status_code=401)

            #Recupera l'alias e il ruolo dal database usando l'username
            user_data = users_collection.find_one({"t_username": username})
            if not user_data:
                return func.HttpResponse("Utente non trovato.", status_code=404)

            alias = user_data.get("t_alias_generated")
            role = user_data.get("t_role")

            if not alias or not role:
                return func.HttpResponse("Dati dell'utente mancanti.", status_code=400)

            # Controlla se il ruolo è valido
            if role not in ALLOWED_ROLES:
                return func.HttpResponse("Ruolo dell'utente non valido.", status_code=400)

            # Ottieni i dati dalla richiesta
            try:
                req_body = req.get_json()
                ticket_id = req_body.get('support_ticket_id')
                body = req_body.get('body')
                attachments = req_body.get('attachments', [])
                new_status = req_body.get('status')
            except ValueError:
                return func.HttpResponse("Richiesta non valida.", status_code=400)

            # Controlla se i campi obbligatori sono presenti
            if not all([ticket_id, body, new_status]):
                return func.HttpResponse("Dati mancanti per la risposta o stato.", status_code=400)

            # Crea un nuovo record per la risposta
            response = {
                "support_ticket_id": ObjectId(ticket_id),
                "alias": alias,
                "role": role,
                "replyDateHour": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "body": body,
                "attachments": attachments
            }

            # Inserisce la risposta nel database
            support_ticket_discussion_collection.insert_one(response)

            # Aggiorna lo stato del ticket
            support_ticket_collection.update_one(
                {"_id": ObjectId(ticket_id)},
                {"$set": {"status": new_status}}
            )

            response_body = json.dumps({"message": "Risposta aggiunta con successo"})
            return func.HttpResponse(
                body=response_body,
                status_code=201,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante l'aggiunta della risposta.", status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
