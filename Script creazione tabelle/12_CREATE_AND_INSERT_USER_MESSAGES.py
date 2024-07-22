import os
import pymongo
import random
import string
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from dotenv import load_dotenv

load_dotenv()
# Carica le variabili di ambiente
load_dotenv()

# Connessione al database MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
users_collection = db.Users
messages_collection = db.Messages

def random_string(length=50):
    """Genera una stringa casuale di una lunghezza specificata"""
    return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))

def create_messages():
    """Crea conversazioni tra utenti"""
    # Recupera gli utenti con il ruolo 'Utente'
    users = list(users_collection.find({"t_role": "Utente"}))
    if len(users) < 2:
        print("Non ci sono abbastanza utenti per creare conversazioni.")
        return

    for _ in range(50):  # Crea 10 conversazioni
        user_from = random.choice(users)["t_username"]
        user_at = random.choice([user["t_username"] for user in users if user["t_username"] != user_from])
        
        message = random_string(random.randint(20, 100))  # Messaggio casuale tra 20 e 100 caratteri

        conversation = {
            "user_from": user_from,
            "user_at": user_at,
            "message": message,
            "dateTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        messages_collection.insert_one(conversation)
        print(f"Conversazione creata: {conversation}")

if __name__ == "__main__":
    create_messages()
