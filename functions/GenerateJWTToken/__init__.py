import logging
import os
import pymongo
import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
import azure.functions as func
from werkzeug.security import check_password_hash
import json  # Importa il modulo json per la serializzazione

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = ("mongodb://unieventcosmosdb"
                 ":a1MoJYXGpXTf2Rgz1KoFFrMnlxLSEnyZmQ5f5WhQeXt1B99VN1LkKmllq2sIN4ueFA0ZevjRhQjZACDbwgZgDA"
                 "==@unieventcosmosdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb"
                 "&maxIdleTimeMS=120000&appName=@unieventcosmosdb@")

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
    secret_key = os.environ.get('JWT_SECRET_KEY', '96883c431142be979c69509655c4eca623a34714f948206b0cfbed0e986b173e')

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

    return token # Decodifica il token in una stringa


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
            user = verify_user(t_username, t_password)

            if user:
                # Genera il token JWT
                jwt_token = generate_jwt_token(user)

                # Costruisci il corpo della risposta come una stringa JSON
                response_body = json.dumps({ "token": jwt_token })

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
