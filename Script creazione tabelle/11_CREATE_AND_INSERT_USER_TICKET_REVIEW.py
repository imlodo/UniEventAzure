import os
import pymongo
import random
import string
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# Connessione al database MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
tickets_collection = db.Tickets
ticket_reviews_collection = db.TicketReviews

def random_string(length=10):
    """Genera una stringa casuale di una lunghezza specificata"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_star():
    """Genera un valore di stelle casuale tra 0.5 e 5 con incrementi di 0.5"""
    return round(random.uniform(0.5, 5.0) * 2) / 2

def create_ticket_reviews():
    """Crea recensioni per ogni biglietto associato a un utente"""
    tickets = tickets_collection.find()

    for ticket in tickets:
        ticket_id = ticket["_id"]
        username = ticket["t_username"]
        event_id = ticket["event_id"]
        
        review = {
            "t_username": username,
            "t_ticket_id": ticket_id,
            "t_event_id": event_id,
            "t_title": f"Review {random_string(10)}",
            "t_body": f"This is a review body for the ticket {ticket_id}. {random_string(50)}",
            "n_star": random_star(),
            "review_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "created_date": datetime.utcnow().strftime("%Y-%m-%d")
        }

        ticket_reviews_collection.insert_one(review)
        print(f"Recensione creata: {review}")

create_ticket_reviews()
