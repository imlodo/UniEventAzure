import logging
import os
from datetime import datetime, timedelta
from random import random

import pymongo
from pymongo import MongoClient
import azure.functions as func
import jwt
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
user_verify_collection = db.UserVerify

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


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

            # Estrai i campi dal corpo della richiesta
            name = req_body.get('name')
            surname = req_body.get('surname')
            birthdate = req_body.get('birthdate')
            pIva = req_body.get('pIva')
            companyName = req_body.get('companyName')
            companyAddress = req_body.get('companyAddress')
            pec = req_body.get('pec')
            consentClauses = req_body.get('consentClauses')
            identity_document = req_body.get('identity_document')
            status = req_body.get('status')
            refused_motivation = req_body.get('refused_motivation')

            # Controlla che i campi obbligatori siano presenti
            if not (
                    name and surname and birthdate and pIva and pec and consentClauses is not None and identity_document and status):
                return func.HttpResponse(
                    "Tutti i campi obbligatori devono essere forniti.",
                    status_code=400
                )

            # Verifica se l'utente esiste già
            user = user_verify_collection.find_one({"t_username": t_username})
            today_date = datetime.now().date()

            if user:
                existing_status = user.get('status')
                refused_date = user.get('refused_date')

                if existing_status == 'refused' and refused_date and today_date >= (refused_date + timedelta(days=90)):
                    # Aggiorna il record
                    update_fields = {
                        "name": name,
                        "surname": surname,
                        "birthdate": birthdate,
                        "pIva": pIva,
                        "companyName": companyName,
                        "companyAddress": companyAddress,
                        "pec": pec,
                        "consentClauses": consentClauses,
                        "identity_document": identity_document,
                        "status": "requested",
                        "refused_date": None,
                        "refused_motivation": None
                    }
                    user_verify_collection.update_one({"t_username": t_username}, {"$set": update_fields})
                elif existing_status == 'requested' and (status == "refused" or status == "verified"):
                    update_fields = {
                        "name": name,
                        "surname": surname,
                        "birthdate": birthdate,
                        "pIva": pIva,
                        "companyName": companyName,
                        "companyAddress": companyAddress,
                        "pec": pec,
                        "consentClauses": consentClauses,
                        "identity_document": identity_document,
                        "status": status,
                        "refused_date": datetime.now().date() if status == "refused" else None,
                        "refused_motivation": refused_motivation
                    }
                    user_verify_collection.update_one({"t_username": t_username}, {"$set": update_fields})
                else:
                    # Rifiuta la chiamata
                    return func.HttpResponse("Utente esistente con stato non aggiornabile", status_code=400)
            else:
                # Inserisci un nuovo record
                new_user = {
                    "t_username": t_username,
                    "name": name,
                    "surname": surname,
                    "birthdate": birthdate,
                    "pIva": pIva,
                    "companyName": companyName,
                    "companyAddress": companyAddress,
                    "pec": pec,
                    "consentClauses": consentClauses,
                    "identity_document": identity_document,
                    "status": "requested",
                    "refused_date": None
                }
                user_verify_collection.insert_one(new_user)

            return func.HttpResponse(json.dumps({"message":"Operazione completata con successo"}), status_code=200)

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse("Errore durante l'elaborazione della richiesta", status_code=500)

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )
