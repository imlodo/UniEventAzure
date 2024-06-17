import pymongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
import re

class USER_TYPE(Enum):
    ARTIST = "ARTIST"
    CREATOR = "CREATOR"
    COMPANY = "COMPANY"

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = ("mongodb://unieventcosmosdb"
                 ":a1MoJYXGpXTf2Rgz1KoFFrMnlxLSEnyZmQ5f5WhQeXt1B99VN1LkKmllq2sIN4ueFA0ZevjRhQjZACDbwgZgDA"
                 "==@unieventcosmosdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb"
                 "&maxIdleTimeMS=120000&appName=@unieventcosmosdb@")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
users_collection = db.User

# Creare un indice unico su t_alias_generated
users_collection.create_index("t_alias_generated", unique=True)
users_collection.create_index("t_username", unique=True)

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
def add_user(username, password, name, surname, description, profile_photo, is_verified, user_type):
    password_hash = generate_password_hash(password)
    alias = generate_unique_alias(name, surname)
    user = {
        "t_username": username,
        "t_password": password_hash,
        "t_name": name,
        "t_surname": surname,
        "t_alias_generated": alias,
        "t_description": description,
        "t_profile_photo": profile_photo,
        "is_verified": is_verified,
        "t_type": user_type.value
    }
    try:
        users_collection.insert_one(user)
        print(f"Utente {username} aggiunto con successo con alias '{alias}'.")
    except pymongo.errors.DuplicateKeyError:
        print(f"Errore: l'alias '{alias}' è già in uso.")

# Funzione per verificare la password di un utente
def verify_user(alias, password):
    user = users_collection.find_one({"t_alias_generated": alias})
    if user and check_password_hash(user['t_password'], password):
        return True
    return False

# Aggiungi tre utenti di esempio, uno per ogni tipo di USER_TYPE
add_user(
    username="artist_user",
    password="artist_password",
    name="Leonardo",
    surname="Da Vinci",
    description="A renowned artist",
    profile_photo="https://example.com/leonardo.jpg",
    is_verified=True,
    user_type=USER_TYPE.ARTIST
)

add_user(
    username="creator_user",
    password="creator_password",
    name="Marie",
    surname="Curie",
    description="A pioneering researcher",
    profile_photo="https://example.com/marie.jpg",
    is_verified=True,
    user_type=USER_TYPE.CREATOR
)

add_user(
    username="company_user",
    password="company_password",
    name="Tech",
    surname="Inc.",
    description="A leading technology company",
    profile_photo="https://example.com/tech.jpg",
    is_verified=True,
    user_type=USER_TYPE.COMPANY
)

# Verifica delle password degli utenti
print("Verifica password per 'leonardodavinci':", verify_user("leonardodavinci", "artist_password"))  # Output: True
print("Verifica password per 'mariecurie':", verify_user("mariecurie", "creator_password"))  # Output: True
print("Verifica password per 'techinc':", verify_user("techinc", "company_password"))  # Output: True

# Verifica con password sbagliate
print("Verifica password errata per 'leonardodavinci':", verify_user("leonardodavinci", "wrong_password"))  # Output: False
print("Verifica password errata per 'mariecurie':", verify_user("mariecurie", "wrong_password"))  # Output: False
print("Verifica password errata per 'techinc':", verify_user("techinc", "wrong_password"))  # Output: False
