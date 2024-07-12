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
users_collection = db.Users
messages_collection = db.Messages
user_settings_collection = db.USER_SETTINGS
follow_user_collection = db.FollowUser

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

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


def get_user_settings(t_username):
    user_settings = user_settings_collection.find_one({"t_username": t_username})
    if user_settings:
        return user_settings
    return None


def is_account_private(t_username):
    user_settings = get_user_settings(t_username)
    if user_settings:
        private_account_path = SETTINGS_MAPPING["PRIVATE_ACCOUNT_TOGGLE"]
        keys = private_account_path.split(".")
        value = user_settings
        for key in keys:
            value = value.get(key, None)
            if value is None:
                break
        return value == True
    return False


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

            # Ottieni i dati dalla richiesta
            try:
                req_body = req.get_json()
                alias_generated = req_body.get('t_alias_generated')
                message = req_body.get('message')
            except ValueError:
                return func.HttpResponse("Richiesta non valida.", status_code=400)

            # Controlla se i campi obbligatori sono presenti
            if not all([alias_generated, message]):
                return func.HttpResponse("Dati mancanti per il messaggio.", status_code=400)

            # Recupera l'utente di destinazione dal database tramite l'alias generato
            # user_at = users_collection.find_one({"t_alias_generated": alias_generated})
            # if not user_at:
            #     return func.HttpResponse("Utente destinatario non trovato.", status_code=404)

            # is_account_private_bool = is_account_private(user_at['t_username'])
            # 
            # if is_account_private_bool:
            #     user_from = users_collection.find_one({"t_username": username})
            #     #Verifica se l'utente 'from' segue l'utente 'to'
            #     follow_record_1 = follow_user_collection.find_one({
            #         "t_alias_generated_from": user_from.get("t_alias_generated"),
            #         "t_alias_generated_to": t_alias_generated
            #     })
            #     follow_record_2 = follow_user_collection.find_one({
            #         "t_alias_generated_from": t_alias_generated,
            #         "t_alias_generated_to": user_from.get("t_alias_generated"),
            #     })
            #     if not follow_record_1 or not follow_record_2:
            #         return func.HttpResponse("Non puoi inviare il messaggio, l'account dell'utente è privato, dovete seguirvi a vicenda.", status_code=400)

            new_message = {
                "user_from": username,
                "user_at": "",  #user_at['t_username'],
                "message": message,
                "dateTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }

            # Inserisce il nuovo messaggio nel database
            #messages_collection.insert_one(new_message)

            response_body = json.dumps({"message": "Messaggio inviato con successo."})
            return func.HttpResponse(
                body=response_body,
                status_code=201,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante l'invio del messaggio.", status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
