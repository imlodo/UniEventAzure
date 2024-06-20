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

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Ottieni la stringa di connessione dal file delle variabili d'ambiente
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
users_collection = db.User

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Funzione per verificare le credenziali dell'utente
def verify_user(t_username, password):
    user = users_collection.find_one({"t_username": t_username})
    if user and check_password_hash(user['t_password'], password):
        # Rimuovi il campo password dall'oggetto utente
        del user['t_password']
        return user
    return None


# Funzione per generare un token JWT
def generate_jwt_token(user):
    # Configura la chiave segreta (da mantenere in un ambiente sicuro)
    secret_key = os.getenv('JWT_SECRET_KEY')

    # Scadenza del token (2 ore)
    expiration = datetime.utcnow() + timedelta(minutes=120)

    # Creazione del payload del token
    payload = {
        'user_id': str(user['_id']),  # Assumendo che l'ID utente sia un ObjectId
        'username': user['t_username'],
        'exp': expiration
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

            # Estrai t_username e t_password dal corpo della richiesta
            t_username = req_body.get('t_username')
            t_password = req_body.get('t_password')

            if not t_username or not t_password:
                return func.HttpResponse(
                    "Inserire t_username e t_password nel corpo della richiesta.",
                    status_code=400
                )

            # Verifica le credenziali dell'utente nel database
            # user = verify_user(t_username, t_password)

            # Mock user per scopi di esempio
            user = dict(_id="012933923", t_username="johndoe", t_password="hashed_password", t_name="John",
                        t_surname="Doe",
                        t_alias_generated="JD", t_description="Lorem ipsum dolor sit amet.",
                        t_profile_photo="http://localhost:4200/assets/img/userExampleImg.jpeg", is_verified=True,
                        t_type="CREATOR")

            if user:
                # Genera il token JWT
                jwt_token = generate_jwt_token(user)

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
