import logging
import os
import json

import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient
import azure.functions as func
from werkzeug.security import generate_password_hash
import re
from enum import Enum

# Carica le variabili di ambiente dal file .env
load_dotenv()


# Enum per il tipo di utente
class USER_TYPE(Enum):
    ARTIST = "ARTIST"
    CREATOR = "CREATOR"
    COMPANY = "COMPANY"


# Enum per il ruolo dell'utente
class USER_ROLE(Enum):
    UTENTE = "Utente"
    MODERATORE = "Moderatore"
    SUPERMODERATORE = "Super Moderatore"


# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
users_collection = db.User


# Funzione per generare un alias univoco
def generate_unique_alias(name, surname):
    base_alias = (name + surname).lower()
    # Rimuovi spazi e caratteri speciali dall'alias
    base_alias = re.sub(r'\W+', '', base_alias)
    alias = base_alias
    counter = 1
    while users_collection.find_one({"t_alias_generated": alias}):
        alias = f"{base_alias}{counter}"
        counter += 1
    return alias


# Funzione per aggiungere un utente
def add_user(data):
    password_hash = generate_password_hash(data['t_password'])
    alias = generate_unique_alias(data['t_name'], data['t_surname'])
    user = {
        "t_username": data.get('t_username'),
        "t_password": password_hash,
        "t_name": data['t_name'],
        "t_surname": data.get('t_surname'),
        "t_alias_generated": alias,
        "is_verified": data.get('is_verified', False),  # Rendere obbligatorio
        "t_type": data['t_type']
    }
    try:
        users_collection.insert_one(user)
        logging.info(f"Utente {data.get('t_username')} aggiunto con successo con alias '{alias}'.")
        return True, user
    except pymongo.errors.DuplicateKeyError:
        logging.error(f"Errore: l'alias '{alias}' è già in uso.")
        return False, "Alias già in uso"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        try:
            # Ottieni i dati dalla richiesta
            try:
                req_body = req.get_json()
                t_username = req_body.get('t_username')
                t_password = req_body.get('t_password')
                t_name = req_body.get('t_name')
                t_birthdate = req_body.get('t_birthdate')
                t_surname = req_body.get('t_surname')
                t_type = req_body.get('t_type')
                is_verified = False
            except ValueError:
                return func.HttpResponse("Richiesta non valida.", status_code=400)

            if not all([t_username, t_password, t_name, t_type, t_birthdate]):
                return func.HttpResponse("Dati mancanti per creare l'utente.", status_code=400)

            # Aggiungi l'utente
            user_data = {
                "t_username": t_username,
                "t_password": t_password,
                "t_name": t_name,
                "t_surname": t_surname,
                "t_birthdate": t_birthdate,
                "t_type": str(USER_TYPE[t_type]),
                "is_verified": is_verified,
                "t_role": str(USER_ROLE.UTENTE)
            }
            success, result = True, user_data  #add_user(user_data)
            if success:
                return func.HttpResponse(
                    json.dumps({"message":"Account creato con successo"}),
                    mimetype="application/json",
                    status_code=201
                )
            else:
                return func.HttpResponse("Si è verificato un errore durante la creazione dell'utente.", status_code=400)


        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Si è verificato un errore durante la creazione dell'utente.", status_code=500)

    else:
        return func.HttpResponse("Metodo non supportato. Utilizzare il metodo POST.", status_code=405)
