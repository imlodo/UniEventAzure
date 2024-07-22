import logging
import os
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

# Seleziona la collezione per le recensioni dei biglietti
reviews_collection = db.TicketReviews

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

# Funzione per convertire i documenti MongoDB in JSON serializzabili
def serialize_document(doc):
    if isinstance(doc, dict):
        return {k: serialize_document(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_document(i) for i in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

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

            # Ottieni i dati dalla query string
            ticket_id = req.params.get('t_ticket_id')
            use_username = req.params.get('use_username', 'true').lower() == 'true'

            if not ticket_id:
                return func.HttpResponse("ID del biglietto mancante.", status_code=400)

            if use_username:
                # Recupera la recensione specifica se viene passato username e t_ticket_id
                review = reviews_collection.find_one({"t_username": username, "t_ticket_id": ObjectId(ticket_id)}, {"_id": 0})
                if review:
                    return func.HttpResponse(body=json.dumps(serialize_document(review)), status_code=200, mimetype='application/json')
                else:
                    return func.HttpResponse("Nessuna recensione trovata per questo biglietto e utente.", status_code=404)
            else:
                # Recupera la lista delle recensioni per un determinato biglietto se viene passato solo t_ticket_id
                reviews = list(reviews_collection.find({"t_ticket_id": ticket_id}, {"_id": 0}))
                if reviews:
                    return func.HttpResponse(body=json.dumps(serialize_document(reviews)), status_code=200, mimetype='application/json')
                else:
                    return func.HttpResponse("Nessuna recensione trovata per questo biglietto.", status_code=404)

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante il controllo della recensione.", status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo GET.", status_code=405)
