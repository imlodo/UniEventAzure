import os
import pymongo
import random
import string
from pymongo import MongoClient
from faker import Faker  # Usato per generare dati fittizi
from dotenv import load_dotenv

load_dotenv()
# Connessione al database MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
users_collection = db.Users
user_cards_collection = db.UserCards

# Inizializza Faker per la generazione di dati fittizi
faker = Faker()

def generate_card_number():
    """Genera un numero di carta di credito fittizio"""
    return ''.join(random.choices(string.digits, k=16))

def generate_cvv():
    """Genera un CVV fittizio"""
    return ''.join(random.choices(string.digits, k=3))

def create_user_cards():
    # Recupera utenti con ruolo ARTIST, CREATOR e COMPANY
    roles = ["ARTIST", "CREATOR", "COMPANY"]
    users = list(users_collection.find({"t_role": "Utente"}))  # Modificato per "Utente"
    
    if not users:
        print("Nessun utente trovato con il ruolo specificato.")
        return

    # Crea una carta per ogni utente recuperato
    for user in users:
        t_alias_generated = user.get("t_alias_generated")
        card_name = faker.credit_card_provider()
        card_number = generate_card_number()
        expiry_date = faker.credit_card_expire()
        cvv = generate_cvv()

        user_card_record = {
            "t_alias_generated": t_alias_generated,
            "cardName": card_name,
            "cardNumber": card_number,
            "expiryDate": expiry_date,
            "cvv": cvv
        }

        user_cards_collection.insert_one(user_card_record)
        print(f"Carta dell'utente inserita: {user_card_record}")

if __name__ == "__main__":
    create_user_cards()
