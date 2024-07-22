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
support_tickets_collection = db.SupportTickets
users_collection = db.Users

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

            # Recupera i ticket di supporto dal database
            user = users_collection.find_one({"t_username": username})
            if user and user.get("t_role") != "Utente":
                tickets = support_tickets_collection.find()
            else:
                tickets = support_tickets_collection.find({"t_username": username})

            ticket_list = []

            # Ottieni la data odierna
            today = datetime.utcnow()

            for ticket in tickets:
                # Verifica se expired_date è già un oggetto datetime
                expired_date = ticket.get("expired_date")
                if isinstance(expired_date, datetime):
                    isScaduto = expired_date < today
                    formatted_expired_date = expired_date.strftime("%d/%m/%Y")
                else:
                    # Se expired_date è una stringa, convertila
                    expired_date = datetime.strptime(expired_date, "%Y-%m-%d")
                    isScaduto = expired_date < today
                    formatted_expired_date = expired_date.strftime("%d/%m/%Y")

                ticket_detail = {
                    "t_username": ticket.get("t_username"),
                    "id": str(ticket.get("_id")),
                    "description": ticket.get("description"),
                    "status": ticket.get("status"),
                    "expired_date": formatted_expired_date,
                    "isScaduto": isScaduto
                }

                ticket_list.append(ticket_detail)

            response_body = json.dumps(ticket_list)
            return func.HttpResponse(
                body=response_body,
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante il recupero dei ticket di supporto.", status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo GET.", status_code=405)
