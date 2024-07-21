import os
import pymongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import random
import string

# Connessione al cluster di MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e la collezione
db = client.unieventmongodb
users_collection = db.Users

# Dati di esempio per gli utenti
topics_aliases = ["davidestrianese", "mariobaldi", "francescoferrara"]
events_aliases_company = ["discosalerno", "discominori"]
events_aliases_artist = ["chiaraferragni", "salmo"]
moderators_aliases = ["moderator1", "moderator2", "moderator3"]
super_moderators_aliases = ["supermoderator1", "supermoderator2", "supermoderator3"]

# Ruoli e tipi utente
roles = ["Utente", "Moderatore", "Super Moderatore"]
user_types_creator = ["CREATOR"]
user_types_company = ["COMPANY"]
user_types_artist = ["ARTIST"]

# Funzione per generare una stringa casuale per la password
def random_string(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Inserisci utenti
def insert_users():
    users = []
    
    # Genera utenti per Topics
    for alias in topics_aliases:
        user = {
            "t_username": f"{alias}_{random.randint(1, 1000)}",
            "t_password": random_string(12),  # Password non cifrata
            "t_name": alias.split(' ')[0].capitalize(),
            "t_surname": alias.split(' ')[-1].capitalize(),
            "t_alias_generated": alias,
            "is_verified": random.choice([True, False]),
            "t_type": "CREATOR",
            "t_role": random.choice(roles)
        }
        user["t_password"] = generate_password_hash(user["t_password"])  # Hash della password
        users.append(user)
    
    # Genera utenti per Eventi - COMPANY
    for alias in events_aliases_company:
        user = {
            "t_username": f"{alias}_{random.randint(1, 1000)}",
            "t_password": random_string(12),  # Password non cifrata
            "t_name": alias.split(' ')[0].capitalize(),
            "t_surname": alias.split(' ')[-1].capitalize(),
            "t_alias_generated": alias,
            "is_verified": random.choice([True, False]),
            "t_type": "COMPANY",
            "t_role": random.choice(roles)
        }
        user["t_password"] = generate_password_hash(user["t_password"])  # Hash della password
        users.append(user)

    # Genera utenti per Eventi - ARTIST (solo verificati)
    for alias in events_aliases_artist:
        user = {
            "t_username": f"{alias}_{random.randint(1, 1000)}",
            "t_password": random_string(12),  # Password non cifrata
            "t_name": alias.split(' ')[0].capitalize(),
            "t_surname": alias.split(' ')[-1].capitalize(),
            "t_alias_generated": alias,
            "is_verified": True,
            "t_type": "ARTIST",
            "t_role": random.choice(roles)
        }
        user["t_password"] = generate_password_hash(user["t_password"])  # Hash della password
        users.append(user)

    # Genera utenti per Moderatori e Super Moderatori
    all_moderators_aliases = moderators_aliases + super_moderators_aliases
    for alias in all_moderators_aliases:
        role = "Moderatore" if alias in moderators_aliases else "Super Moderatore"
        user = {
            "t_username": f"{alias}_{random.randint(1, 1000)}",
            "t_password": random_string(12),  # Password non cifrata
            "t_name": alias.split(' ')[0].capitalize(),
            "t_surname": alias.split(' ')[-1].capitalize(),
            "t_alias_generated": alias,
            "is_verified": random.choice([True, False]),
            "t_type": random.choice(user_types_creator),  # Solo CREATOR per Moderatori e Super Moderatori
            "t_role": role
        }
        user["t_password"] = generate_password_hash(user["t_password"])  # Hash della password
        users.append(user)
    
    # Inserisci i documenti nella collezione
    users_collection.insert_many(users)
    
    # Stampa gli utenti e le password non cifrate
    for user in users:
        print(f"Username: {user['t_username']}, Password: {user['t_password'].replace('pbkdf2:sha256:50000$', '')}")  # Rimuove l'hash dalla stampa

# Esegui lo script di inserimento
insert_users()
