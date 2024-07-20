import logging
import os
from random import random

import jwt
import json
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

# Seleziona la collezione (crea la collezione se non esiste)
user_settings_collection = db.UserSettings
follow_user_collection = db.FollowUser
follow_user_request_collection = db.FollowUserRequest
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

# Mappa le impostazioni possibili ai rispettivi campi nel documento
SETTINGS_MAPPING = {
    "PRIVATE_ACCOUNT_TOGGLE": "privacy.visibility.private_account",
    "SHOW_BOOKED_TOGGLE": "privacy.visibility.show_booked",
    "MESSAGE_TOGGLE": "privacy.messages.all_user_send_message",
    "DESKTOP_NOTIFICATION_TOGGLE": "notification.desktop.browser_consent",
    "INTERACTION_LIKE_TOGGLE": "notification.interaction.like",
    "INTERACTION_DISCUSSION_TOGGLE": "notification.interaction.comments",
    "INTERACTION_TAG_TOGGLE": "notification.interaction.tag",
    "INTERACTION_NEW_FOLLOWER_TOGGLE": "notification.interaction.new_follower_request",
    "INTERACTION_SUGGEST_FOLLOWER_TOGGLE": "notification.interaction.follower_suggest",
    "INTERACTION_TERMS_AND_CONDITION_TOGGLE": "notification.interaction.terms_and_condition",
    "INTERACTION_PAYMENTS_TOGGLE": "notification.interaction.payments",
    "INTERACTION_TICKETS_TOGGLE": "notification.interaction.tickets"
}


def update_user_settings(t_username, setting_type, value):
    # Trova l'impostazione corrispondente
    if setting_type not in SETTINGS_MAPPING:
        raise ValueError(f"Invalid setting type: {setting_type}")

    setting_path = SETTINGS_MAPPING[setting_type]
    user = users_collection.find_one({"t_username": t_username})

    if not user:
        raise ValueError(f"User not found: {t_username}")

    t_alias_generated = user.get("t_alias_generated")

    if setting_path == "privacy.visibility.private_account" and value is True:
        follow_user_requests = follow_user_request_collection.find({"t_alias_generated_to": t_alias_generated})

        for request in follow_user_requests:
            t_alias_generated_from = request.get("t_alias_generated_from")
            follow_user_record = {
                "t_alias_generated_to": t_alias_generated,
                "t_alias_generated_from": t_alias_generated_from
            }
            follow_user_collection.insert_one(follow_user_record)

    # Converti il path in dot notation in un dict per $set
    update_query = {setting_path: value}

    result = user_settings_collection.update_one(
        {"t_username": t_username},
        {"$set": update_query}
    )

    return result.modified_count > 0


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
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
                return func.HttpResponse(
                    "Token scaduto.",
                    status_code=401
                )
            except jwt.InvalidTokenError:
                return func.HttpResponse(
                    "Token non valido.",
                    status_code=401
                )

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    "Token non contiene un username valido.",
                    status_code=401
                )

            # Prova a ottenere i dati JSON dal corpo della richiesta
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    "La richiesta non contiene dati JSON validi.",
                    status_code=400
                )

            # Estrai il tipo di impostazione e il valore dal corpo della richiesta
            setting_type = req_body.get('setting_type')
            value = req_body.get('value')
            if not setting_type or value is None:
                return func.HttpResponse(
                    "Inserire setting_type e value nel corpo della richiesta.",
                    status_code=400
                )

            # Esegui l'aggiornamento delle impostazioni utente nel database
            try:
                if random() > 0.5:  #update_user_settings(t_username, setting_type, value):
                    response_body = json.dumps({"message": "Impostazioni aggiornate con successo."})
                    return func.HttpResponse(
                        body=response_body,
                        status_code=200,
                        mimetype='application/json'
                    )
                else:
                    return func.HttpResponse(
                        "Nessun aggiornamento eseguito. Controlla che i dati siano corretti.",
                        status_code=404
                    )
            except ValueError as e:
                return func.HttpResponse(
                    str(e),
                    status_code=400
                )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante l'aggiornamento delle impostazioni utente.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )
