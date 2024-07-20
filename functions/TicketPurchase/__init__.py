import logging
import os
import random

import pymongo
import jwt
import azure.functions as func
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)
db = client.unieventmongodb
tickets_collection = db.Tickets
users_collection = db.Users
events_collection = db.Contents
user_cards_collection = db.UserCards
user_addresses_collection = db.UserAddresses
event_coupons_collection = db.EventCoupon

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    "Token non fornito o non valido.",
                    status_code=401
                )

            jwt_token = auth_header.split(' ')[1]
            secret_key = os.getenv('JWT_SECRET_KEY')

            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    "Token scaduto.",
                    status_code=401
                )
            except jwt.InvalidTokenError:
                return func.HttpResponse(
                    "Token non valido.",
                    status_code=401
                )

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    "Token non contiene un username valido.",
                    status_code=401
                )

            # Recupera l'utente dal database usando t_username
            # user = users_collection.find_one({"t_username": t_username})
            # if not user:
            #     return func.HttpResponse(
            #         "Utente non trovato.",
            #         status_code=404
            #     )

            req_body = req.get_json()

            event_id = req_body.get('event_id')
            card_id = req_body.get('card_id')
            address_id = req_body.get('address_id')
            coupon_id = req_body.get('coupon_id')
            eventTicketList = req_body.get('eventTicketList')

            if not (event_id and card_id and address_id and eventTicketList):
                return func.HttpResponse(
                    "Parametri mancanti nel corpo della richiesta.",
                    status_code=400
                )

            # # Verifica l'evento
            # event = events_collection.find_one({"_id": ObjectId(event_id)})
            # if not event:
            #     return func.HttpResponse(
            #         "Evento non trovato.",
            #         status_code=404
            #     )

            # Verifica la carta
            # card = user_cards_collection.find_one(
            #     {"_id": ObjectId(card_id), "t_alias_generated": user['t_alias_generated']})
            # if not card:
            #     return func.HttpResponse(
            #         "Carta non trovata.",
            #         status_code=404
            #     )

            # Verifica l'indirizzo
            # address = user_addresses_collection.find_one(
            #     {"_id": ObjectId(address_id), "t_alias_generated": user['t_alias_generated']})
            # if not address:
            #     return func.HttpResponse(
            #         "Indirizzo non trovato.",
            #         status_code=404
            #     )

            # Verifica il coupon (se presente)
            discount = 0
            #mock
            discount = 20
            # if coupon_id:
            #     coupon = event_coupons_collection.find_one({"_id": ObjectId(coupon_id)})
            #     if coupon:
            #         discount = coupon.get('discount', 0)

            # Verifica e calcola il prezzo totale dei biglietti
            total_price = 0
            for ticket in eventTicketList:
                if ticket.get('is_acquistabile') and not ticket_altered(ticket):
                    total_price += ticket.get('n_object_price', 0)

            # Applica il coupon (sconto)
            total_price = total_price - (total_price * (discount / 100))
            total_price = round(total_price, 2)

            # Effettua il pagamento (logica del pagamento non inclusa in questo esempio)
            payment_status = process_payment(None, total_price) #process_payment(card, total_price)
            ticket_status = "Confermato" if payment_status else "Rifiutato"

            # Crea il record del biglietto
            ticket_record = {
                "status": ticket_status,
                "creation_date": datetime.utcnow().isoformat(),
                "ticket_type": eventTicketList[0].get('t_type'),
                # Assumendo che tutti i biglietti siano dello stesso tipo
                "price": total_price,
                "event_id": event_id,
                "address_id": address_id,
                "card_id": card_id,
                "coupon_id": coupon_id
            }

            # result = tickets_collection.insert_one(ticket_record)
            # ticket_record['ticket_id'] = str(result.inserted_id)
            
            #MOCK
            ticket_record = {
                "ticket_id": "60c72b2f9b1d4c3d88f78907",
                "status": "Confermato",
                "creation_date": datetime.utcnow().isoformat(),
                "ticket_type": eventTicketList[0].get('t_type'),
                "price": total_price,
                "event_id": event_id,
                "address_id": address_id,
                "card_id": card_id,
                "coupon_id": coupon_id
            } if payment_status else {
                "ticket_id": "60c72b2f9b1d4c3d88f78907",
                "status": "Rifiutato",
                "creation_date": datetime.utcnow().isoformat(),
                "ticket_type": eventTicketList[0].get('t_type'),
                "price": total_price,
                "event_id": event_id,
                "address_id": address_id,
                "card_id": card_id,
                "coupon_id": coupon_id
            }

            return func.HttpResponse(
                body=json.dumps(ticket_record),
                status_code=201 if payment_status else 400,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Errore: {e}")
            return func.HttpResponse("Errore durante l'elaborazione della richiesta", status_code=500)

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )


def ticket_altered(ticket):
    # Logica per verificare se il ticket è stato alterato
    # devi restituire l'oggetto memorizzato nel db corrispondente a questo passato dall'utente
    return False


def process_payment(card, amount):
    # Logica per pagamento
    return random.random() > 0.1
