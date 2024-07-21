import os
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import string

# Connessione al cluster di MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
users_collection = db.Users
user_verify_collection = db.UserVerify

# Funzione per generare una stringa casuale
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_date(start_date, end_date):
    return start_date + (end_date - start_date) * random.random()

# Inserisci richieste di verifica per gli utenti CREATOR
def insert_user_verification_requests():
    # Trova tutti gli utenti di tipo CREATOR
    creators = users_collection.find({"t_type": "CREATOR"})
    
    user_verifications = []

    # Definisci l'intervallo di date per la generazione
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now() - timedelta(days=1)  # Giorno corrente - 1 giorno

    for creator in creators:
        t_username = creator["t_username"]
        name = creator["t_name"]
        surname = creator["t_surname"]
        
        # Genera dati casuali per la verifica
        birthdate = random_date(start_date, end_date).strftime("%Y-%m-%d")
        pIva = f"IT{random_string(11)}"
        companyName = f"Company_{random_string(5)}"
        companyAddress = f"Address_{random_string(10)}"
        pec = f"pec_{random_string(5)}@example.com"
        consentClauses = random.choice(["consent_1", "consent_2", "consent_3"])
        identity_document = f"doc_{random_string(10)}.pdf"

        verification_request = {
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
        
        user_verifications.append(verification_request)
    
    # Inserisci le richieste di verifica nel database
    if user_verifications:
        user_verify_collection.insert_many(user_verifications)
        print(f"{len(user_verifications)} richieste di verifica inserite con successo.")

# Esegui lo script di inserimento
insert_user_verification_requests()
