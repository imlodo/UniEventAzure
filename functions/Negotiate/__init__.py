import azure.functions as func
import logging
import pymongo
import os

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = pymongo.MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
users_collection = db.User


def username_exists(username):
    user = users_collection.find_one({"t_username": username})
    return user is not None


def main(req: func.HttpRequest, connection) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Ottieni l'username dalla richiesta
    username = req.headers.get('x-ms-client-principal-name')
    if not username:
        return func.HttpResponse(
            "Missing username in headers.",
            status_code=400
        )

    # Verifica se l'username esiste nel database
    # if not username_exists(username):
    #     return func.HttpResponse(
    #         "Username does not exist.",
    #         status_code=404
    #     )

    # Restituisci la connessione WebSocket
    return func.HttpResponse(connection)
