import pymongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# Puoi ottenere la stringa di connessione dal portale di Azure nella sezione delle chiavi di accesso del tuo account Cosmos DB.
# Connessione al cluster di Azure Cosmos DB for MongoDB
client = MongoClient("<YOUR_CONNECTION_STRING>")

# Seleziona il database
db = client.myMongoDB

# Seleziona la collezione (crea la collezione se non esiste)
users_collection = db.User

# Funzione per aggiungere un utente
def add_user(nome, cognome, alias, password):
    password_hash = generate_password_hash(password)
    user = {
        "Nome": nome,
        "Cognome": cognome,
        "t_alias_generated": alias,
        "password": password_hash
    }
    users_collection.insert_one(user)

# Funzione per verificare la password di un utente
def verify_user(alias, password):
    user = users_collection.find_one({"t_alias_generated": alias})
    if user and check_password_hash(user['password'], password):
        return True
    return False

# Aggiungi un utente di esempio
add_user("Mario", "Rossi", "mrossi", "password123")

# Verifica della password dell'utente
is_valid = verify_user("mrossi", "password123")
print("Password valida:", is_valid)  # Output: Password valida: True

# Verifica con una password sbagliata
is_valid_wrong = verify_user("mrossi", "wrongpassword")
print("Password valida con password sbagliata:", is_valid_wrong)  # Output: Password valida con password sbagliata: False
