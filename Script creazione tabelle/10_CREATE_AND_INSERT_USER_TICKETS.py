import os
import pymongo
import random
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# Connessione al database MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
object_maps_collection = db.ObjectMaps
object_seats_collection = db.ObjectSeats
tickets_collection = db.Tickets
user_addresses_collection = db.UserAddresses
user_cards_collection = db.UserCards
event_coupons_collection = db.EventCoupon

def fetch_events_with_object_maps():
    """Recupera eventi con i relativi object_maps"""
    events = db.Contents.find({"t_type": "Eventi"})
    event_object_maps = []

    for event in events:
        event_id = event["_id"]
        object_maps = list(object_maps_collection.find({"t_event_id": event_id}))
        if object_maps:
            event_object_maps.append({
                "event_id": event_id,
                "object_maps": object_maps
            })

    return event_object_maps

def fetch_user_data():
    """Recupera dati degli utenti con indirizzi e carte"""
    addresses = list(user_addresses_collection.find())
    cards = list(user_cards_collection.find())
    return addresses, cards

def fetch_event_coupons(event_id):
    """Recupera i coupon per un evento specifico"""
    return list(event_coupons_collection.find({"event_id": event_id}))

def create_tickets():
    event_object_maps = fetch_events_with_object_maps()
    addresses, cards = fetch_user_data()

    for event_data in event_object_maps:
        event_id = event_data["event_id"]
        object_maps = event_data["object_maps"]
        for obj_map in object_maps:
            object_map_id = obj_map["_id"]
            is_acquistabile = obj_map["is_acquistabile"]
            
            # Recupera i posti associati all'object_map
            seats = list(object_seats_collection.find({"n_object_map_id": object_map_id}))

            # Simula la vendita dei biglietti per posti acquistabili
            for seat in seats:
                if seat["is_sell"]:
                    # Aggiorna l'object_map e i posti
                    object_maps_collection.update_one({"_id": object_map_id}, {"$set": {"is_acquistabile": False}})
                    object_seats_collection.update_one({"_id": seat["_id"]}, {"$set": {"is_acquistabile": False}})
                    
                    # Crea un biglietto
                    ticket = {
                        "status": "Confermato",
                        "creation_date": datetime.utcnow().isoformat(),
                        "ticket_type": obj_map["t_type"],
                        "price": obj_map["n_object_map_price"],
                        "event_id": event_id,
                        "address_id": random.choice(addresses)["_id"],  # Associa un indirizzo casuale
                        "card_id": random.choice(cards)["_id"],  # Associa una carta casuale
                        "coupon_id": random.choice(fetch_event_coupons(event_id))["_id"] if fetch_event_coupons(event_id) else None
                    }

                    tickets_collection.insert_one(ticket)
                    print(f"Biglietto creato: {ticket}")

create_tickets()
