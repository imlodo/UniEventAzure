import os
import pymongo
import random
import json
from pymongo import MongoClient

# Ottieni la stringa di connessione dal file delle variabili d'ambiente
connectString = os.getenv("DB_CONNECTION_STRING")

# Connessione al cluster di MongoDB
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
users_collection = db.Users
user_settings_collection = db.UserSettings

# Definisci le impostazioni predefinite con valori randomici
def generate_random_settings():
    return {
        "privacy": {
            "messages": {
                "all_user_send_message": random.choice([True, False])
            },
            "visibility": {
                "private_account": random.choice([True, False]),
                "show_booked": random.choice([True, False])
            }
        },
        "notification": {
            "desktop": {
                "browser_consent": True
            },
            "interaction": {
                "like": random.choice([True, False]),
                "comments": random.choice([True, False]),
                "tag": random.choice([True, False]),
                "new_follower_request": random.choice([True, False]),
                "follower_suggest": random.choice([True, False]),
                "terms_and_condition": random.choice([True, False]),
                "payments": random.choice([True, False]),
                "tickets": random.choice([True, False])
            }
        }
    }

def initialize_user_settings():
    # Trova tutti gli utenti esclusi quelli con t_role specificato
    excluded_roles = ["Moderatore", "Super Moderatore"]
    query = {"t_role": {"$nin": excluded_roles}}
    
    users = users_collection.find(query)
    
    for user in users:
        t_username = user.get("t_username")
        if t_username:
            settings = generate_random_settings()
            user_settings = {
                "t_username": t_username,
                "settings": settings
            }
            # Inserisci o aggiorna le impostazioni dell'utente nella collezione UserSettings
            user_settings_collection.update_one(
                {"t_username": t_username},
                {"$set": user_settings},
                upsert=True
            )
            print(f"Impostazioni iniziali inserite per l'utente: {t_username}")

# Esegui lo script di inserimento
initialize_user_settings()
