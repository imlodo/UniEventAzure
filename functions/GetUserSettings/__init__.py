import logging
import os
import json
import jwt
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


def get_user_settings(t_username, setting_type=None):
    query = {"t_username": t_username}
    logging.info(f"Query: {query}")
    settings_to_retrieve = {value: 1 for key, value in SETTINGS_MAPPING.items()}
    if setting_type:
        if setting_type.startswith("INTERACTION"):
            settings_to_retrieve = {value: 1 for key, value in SETTINGS_MAPPING.items() if key.startswith(setting_type)}
        else:
            setting_path = SETTINGS_MAPPING.get(setting_type)
            if not setting_path:
                raise ValueError(f"Invalid setting type: {setting_type}")
            settings_to_retrieve = {setting_path: 1}

    logging.info(f"Settings to retrieve: {settings_to_retrieve}")
    
    result = user_settings_collection.find_one({"t_username": t_username})
    logging.info(f"Result: {result}")
    del result["_id"]
    return result["settings"] if result else {}


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
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

            # Ottieni il tipo di impostazione dalla query string
            setting_type = req.params.get('setting_type')

            # Recupera le impostazioni utente dal database
            try:
                settings = get_user_settings(t_username, setting_type)
                logging.info(f"Settings for {t_username}: {settings}")

                return func.HttpResponse(
                    body=json.dumps(settings),
                    status_code=200,
                    mimetype='application/json'
                )
            except ValueError as e:
                return func.HttpResponse(
                    str(e),
                    status_code=400
                )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero delle impostazioni utente.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo GET.",
            status_code=405
        )
