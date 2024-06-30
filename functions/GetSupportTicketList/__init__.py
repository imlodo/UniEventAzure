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

# Seleziona la collezione per i ticket di supporto
support_tickets_collection = db.SupportTickets

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

            # Recupera i ticket di supporto dal database
            # tickets = support_tickets_collection.find({"t_username": username})
            # ticket_list = []
            # 
            # # Ottieni la data odierna
            # today = datetime.utcnow()
            # 
            # for ticket in tickets:
            #     expired_date = datetime.strptime(ticket.get("expired_date"), "%Y-%m-%d")
            #     isScaduto = expired_date < today
            # 
            #     ticket_detail = {
            #         "t_username": ticket.get("t_username"),
            #         "id": ticket.get("id"),
            #         "description": ticket.get("description"),
            #         "status": ticket.get("status"),
            #         "expired_date": expired_date.strftime("%d/%m/%Y"),
            #         "isScaduto": isScaduto
            #     }
            # 
            #     ticket_list.append(ticket_detail)

            ticket_list = [
                {
                    "t_username": "user1",
                    "id": 1,
                    "description": "Problema con l'accesso",
                    "status": "Aperto",
                    "expired_date": "01/01/2024",
                    "isScaduto": False
                },
                {
                    "t_username": "user1",
                    "id": 2,
                    "description": "Errore nella pagina di pagamento",
                    "status": "Attesa Risposta Operatore",
                    "expired_date": "05/01/2024",
                    "isScaduto": False
                },
                {
                    "t_username": "user1",
                    "id": 3,
                    "description": "Richiesta di rimborso",
                    "status": "Chiuso",
                    "expired_date": "20/12/2023",
                    "isScaduto": True
                },
                {
                    "t_username": "user1",
                    "id": 4,
                    "description": "Problema con la registrazione",
                    "status": "Sollecito Riapertura",
                    "expired_date": "22/12/2023",
                    "isScaduto": True
                },
                {
                    "t_username": "user1",
                    "id": 5,
                    "description": "Impossibile aggiornare il profilo",
                    "status": "Necessaria Risposta",
                    "expired_date": "25/12/2023",
                    "isScaduto": True
                },
                {
                    "t_username": "user1",
                    "id": 6,
                    "description": "Errore nella fatturazione",
                    "status": "Aperto",
                    "expired_date": "15/01/2024",
                    "isScaduto": False
                },
                {
                    "t_username": "user1",
                    "id": 7,
                    "description": "Problema con l'invio delle email",
                    "status": "Chiuso",
                    "expired_date": "28/12/2023",
                    "isScaduto": True
                },
                {
                    "t_username": "user1",
                    "id": 8,
                    "description": "Domanda sull'abbonamento",
                    "status": "Attesa Risposta Operatore",
                    "expired_date": "30/12/2023",
                    "isScaduto": True
                },
                {
                    "t_username": "user1",
                    "id": 9,
                    "description": "Problema con il caricamento dei file",
                    "status": "Aperto",
                    "expired_date": "02/02/2024",
                    "isScaduto": False
                },
                {
                    "t_username": "user1",
                    "id": 10,
                    "description": "Richiesta di assistenza tecnica",
                    "status": "Necessaria Risposta",
                    "expired_date": "05/01/2024",
                    "isScaduto": False
                },
                {
                    "t_username": "user1",
                    "id": 11,
                    "description": "Errore 404 su una pagina",
                    "status": "Chiuso",
                    "expired_date": "15/01/2024",
                    "isScaduto": False
                },
                {
                    "t_username": "user1",
                    "id": 12,
                    "description": "Impossibile visualizzare i dati",
                    "status": "Aperto",
                    "expired_date": "10/01/2024",
                    "isScaduto": False
                },
                {
                    "t_username": "user1",
                    "id": 13,
                    "description": "Richiesta di modifica dei dati",
                    "status": "Attesa Risposta Operatore",
                    "expired_date": "05/01/2024",
                    "isScaduto": False
                },
                {
                    "t_username": "user1",
                    "id": 14,
                    "description": "Problema con il download dei file",
                    "status": "Sollecito Riapertura",
                    "expired_date": "25/12/2023",
                    "isScaduto": True
                },
                {
                    "t_username": "user1",
                    "id": 15,
                    "description": "Richiesta di cancellazione dell'account",
                    "status": "Chiuso",
                    "expired_date": "20/12/2023",
                    "isScaduto": True
                }
            ]
            response_body = json.dumps(ticket_list)
            return func.HttpResponse(
                body=response_body,
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante il recupero dei ticket di supporto.",
                                     status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo GET.", status_code=405)
