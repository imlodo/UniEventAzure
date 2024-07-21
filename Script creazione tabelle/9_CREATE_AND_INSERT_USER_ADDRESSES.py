import os
import pymongo
from pymongo import MongoClient
from faker import Faker  # Usato per generare dati fittizi

# Connessione al database MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e la collezione
db = client.unieventmongodb
users_collection = db.Users
user_addresses_collection = db.UserAddresses

# Inizializza Faker per la generazione di dati fittizi
faker = Faker()

def create_user_addresses():
    # Recupera utenti con ruolo ARTIST, CREATOR e COMPANY
    users = list(users_collection.find({"t_role": "Utente"}))  # Modificato per "Utente"
    
    if not users:
        print("Nessun utente trovato con il ruolo specificato.")
        return

    # Crea un indirizzo per ogni utente recuperato
    for user in users:
        t_alias_generated = user.get("t_alias_generated")
        first_name = faker.first_name()
        last_name = faker.last_name()
        street = faker.street_address()
        city = faker.city()
        state = faker.state()
        zip_code = faker.zipcode()

        user_address_record = {
            "t_alias_generated": t_alias_generated,
            "firstName": first_name,
            "lastName": last_name,
            "street": street,
            "city": city,
            "state": state,
            "zip": zip_code
        }

        user_addresses_collection.insert_one(user_address_record)
        print(f"Indirizzo dell'utente inserito: {user_address_record}")

create_user_addresses()
