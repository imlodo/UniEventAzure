import logging
import os
import pymongo
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
import azure.functions as func
from werkzeug.security import check_password_hash
import json
import calendar

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Ottieni la stringa di connessione dal file delle variabili d'ambiente
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

# Funzione per generare un token JWT
def generate_jwt_token(user, t_event_ticket_list):
    # Configura la chiave segreta (da mantenere in un ambiente sicuro)
    secret_key = os.getenv('JWT_SECRET_KEY')

    # Scadenza del token (15 minuti)
    expiration = datetime.utcnow() + timedelta(minutes=15)

    # Per debug: stampa la data di scadenza come stringa
    expiration_str = expiration.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Token expiration time: {expiration_str}")

    # Converti la data di scadenza in timestamp Unix per il payload JWT
    expiration_unix = calendar.timegm(expiration.utctimetuple())

    # Creazione del payload del token
    payload = {
        'username': user['t_username'],
        "t_event_ticket_list": t_event_ticket_list,
        'exp': expiration_unix
    }

    # Genera il token JWT
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return token  # Decodifica il token in una stringa


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Controlla che il metodo della richiesta sia POST
    if req.method == 'POST':
        try:
            # Prova a ottenere i dati JSON dal corpo della richiesta
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    "La richiesta non contiene dati JSON validi.",
                    status_code=400
                )

            # Estrai t_username e t_event_ticket_list dal corpo della richiesta
            t_username = req_body.get('t_username')
            t_event_ticket_list = req_body.get('t_event_ticket_list')

            if not t_username or not t_event_ticket_list:
                return func.HttpResponse(
                    "Inserire t_username e t_event_ticket_list nel corpo della richiesta.",
                    status_code=400
                )

            # user = users_collection.find_one({"t_username": t_username})
            # if not user:
            #     return func.HttpResponse(
            #         "User non trovato.",
            #         status_code=404
            #     )
            # if user.get("active") == False:
            #     return func.HttpResponse(
            #         "Il tuo account è stato eliminato, contatta il supporto.",
            #         status_code=404
            #     )

            # Mock user per scopi di esempio
            user = dict(_id="012933923", t_username="johndoe", t_password="hashed_password", t_name="John",
                        t_surname="Doe",
                        t_alias_generated="JD", t_description="Lorem ipsum dolor sit amet.",
                        t_profile_photo="http://localhost:4200/assets/img/userExampleImg.jpeg", is_verified=True,
                        t_type="CREATOR")

            if user:
                # Genera il token JWT
                jwt_token = generate_jwt_token(user, t_event_ticket_list)

                # Costruisci il corpo della risposta come una stringa JSON
                response_body = json.dumps({"token": jwt_token})

                # Restituisci il token JWT come parte della risposta
                return func.HttpResponse(
                    body=response_body,
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    "Credenziali non valide.",
                    status_code=404
                )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante l'autenticazione.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )
