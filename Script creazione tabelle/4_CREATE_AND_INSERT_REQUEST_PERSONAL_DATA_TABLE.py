import os
import pymongo
from pymongo import MongoClient
from datetime import datetime
import random

# Connessione al cluster di MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
users_collection = db.Users
request_personal_data_collection = db.RequestPersonalData

# Opzioni per il tipo di download e formato
type_download_options = ["ALL_DATA", "CHAT_DATA", "CONTENT_DATA", "BOOKED_DATA", "INTERACTION_DATA"]
type_data_download_options = ["JSON", "TXT"]

# Funzione per generare una richiesta di download
def generate_download_request(user):
    t_username = user["t_username"]
    type_download = random.choice(type_download_options)
    type_data_download = random.choice(type_data_download_options)
    status = "REQUESTED"  # Status iniziale

    request = {
        "t_username": t_username,
        "type_download": type_download,
        "type_data_download": type_data_download,
        "status": status,
        "timestamp": datetime.utcnow(),
        "download_file": None  # Non popolato se lo status è "REQUESTED"
    }
    
    return request

def insert_data_download_requests():
    # Trova tutti gli utenti nel database
    users = list(users_collection.find())
    
    # Calcola il numero minimo di richieste (almeno il 50% degli utenti)
    num_users = len(users)
    min_requests = max(2, num_users // 2)  # Almeno 2 utenti, o metà degli utenti

    # Seleziona casualmente gli utenti per le richieste di download
    selected_users = random.sample(users, min_requests)

    requests = [generate_download_request(user) for user in selected_users]

    # Inserisci le richieste di download nel database
    if requests:
        request_personal_data_collection.insert_many(requests)
        print(f"{len(requests)} richieste di download inserite con successo.")

# Esegui lo script di inserimento
insert_data_download_requests()
