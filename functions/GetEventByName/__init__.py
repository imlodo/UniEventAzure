import logging
import os
import random

import pymongo
import jwt
from azure.functions import HttpResponse
from pymongo import MongoClient
import azure.functions as func
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione (crea la collezione se non esiste)
content_collection = db.Contents

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def search_event_by_caption_liked(event_caption_liked):
    events = content_collection.find({"t_caption": {"$regex": event_caption_liked, "$options": "i"}}).limit(10)
    events_list = []
    for event in events:
        event.pop('_id', None)  # Rimuovi l'ID se presente (per esempio, se è un ObjectId)
        events_list.append(event)
    return events_list


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Controlla che il metodo della richiesta sia GET
    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            t_caption_liked = req.params.get("t_caption_liked")
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    status_code=404
                )

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')

            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    status_code=404
                )
            except jwt.InvalidTokenError:
                return func.HttpResponse(
                    status_code=404
                )

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    status_code=404
                )

            #Cerca gli eventi corrispondenti al parametro t_caption_liked
            # if t_caption_liked:
            #     event_list = search_event_by_caption_liked(t_caption_liked)
            # else:
            #     return func.HttpResponse(
            #         status_code=404
            #     )

            maps =[
                {
                    "t_map_name": "Main Stage",
                    "t_map_event_id": "event123",
                    "t_map_id": 101,
                    "t_map_total_seat": 10,
                    "t_map_num_rows":4,
                    "t_map_num_column":3,
                    "t_object_maps": [
                        {
                            "n_id": 1,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 100,
                            "n_obj_map_cord_x": 0,
                            "n_obj_map_cord_y": 0,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FF0000",
                            "n_obj_map_text": "VIP Section",
                            "t_note": "Closest to the stage",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": False,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 1,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 1,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 2,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 90,
                            "n_obj_map_cord_x": 0,
                            "n_obj_map_cord_y": 1,
                            "n_obj_map_cord_z": 1,
                            "n_obj_map_width": 120,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#00FF00",
                            "n_obj_map_text": "Premium Section",
                            "t_note": "Near the stage",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 2,
                                    "n_id_event": "event123",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 2,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 3,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 80,
                            "n_obj_map_cord_x": 0,
                            "n_obj_map_cord_y": 2,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 120,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#0000FF",
                            "n_obj_map_text": "Regular Section",
                            "t_note": "Middle area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 3,
                                    "n_id_event": "event123",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 3,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 4,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 70,
                            "n_obj_map_cord_x": 0,
                            "n_obj_map_cord_y": 3,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 150,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "black",
                            "n_obj_map_text": "General Admission",
                            "t_note": "Back area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 4,
                                    "n_id_event": "event123",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 4,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 5,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 60,
                            "n_obj_map_cord_x": 1,
                            "n_obj_map_cord_y": 0,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 120,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FF00FF",
                            "n_obj_map_text": "Economy Section",
                            "t_note": "Far back",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 5,
                                    "n_id_event": "event123",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 5,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 6,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 50,
                            "n_obj_map_cord_x": 1,
                            "n_obj_map_cord_y": 1,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 120,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#00FFFF",
                            "n_obj_map_text": "Budget Section",
                            "t_note": "Side area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 6,
                                    "n_id_event": "event123",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 6,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 7,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 40,
                            "n_obj_map_cord_x": 1,
                            "n_obj_map_cord_y": 2,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 130,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FFA500",
                            "n_obj_map_text": "Discount Section",
                            "t_note": "Corner area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 7,
                                    "n_id_event": "event123",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 7,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 8,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 30,
                            "n_obj_map_cord_x": 1,
                            "n_obj_map_cord_y": 3,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#800080",
                            "n_obj_map_text": "Promo Section",
                            "t_note": "Remote area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 8,
                                    "n_id_event": "event123",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 8,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 9,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 20,
                            "n_obj_map_cord_x": 2,
                            "n_obj_map_cord_y": 0,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 120,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#008000",
                            "n_obj_map_text": "Student Section",
                            "t_note": "Upper tier",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 9,
                                    "n_id_event": "event123",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 9,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 10,
                            "n_id_map": 101,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 10,
                            "n_obj_map_cord_x": 2,
                            "n_obj_map_cord_y": 1,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 160,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#000080",
                            "n_obj_map_text": "Economy Plus Section",
                            "t_note": "Nosebleed section",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 10,
                                    "n_id_event": "event123",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 10,
                                    "n_id_event": "event123",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        }
                    ],
                    "t_map_type": "DISCOTECA"
                },
                {
                    "t_map_name": "Second Stage",
                    "t_map_event_id": "event124",
                    "t_map_id": 102,
                    "t_map_total_seat": 20,
                    "t_map_num_rows":5,
                    "t_map_num_column":4,
                    "t_object_maps": [
                        {
                            "n_id": 11,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 110,
                            "n_obj_map_cord_x": 50,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FF0000",
                            "n_obj_map_text": "VIP Section",
                            "t_note": "Closest to the stage",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 11,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 11,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                }
                            ]
                        },
                        {
                            "n_id": 12,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 90,
                            "n_obj_map_cord_x": 60,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#00FF00",
                            "n_obj_map_text": "Premium Section",
                            "t_note": "Near the stage",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 12,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 12,
                                    "n_id_event": "event124",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 13,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 80,
                            "n_obj_map_cord_x": 70,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#0000FF",
                            "n_obj_map_text": "Regular Section",
                            "t_note": "Middle area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 13,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 13,
                                    "n_id_event": "event124",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 14,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 70,
                            "n_obj_map_cord_x": 80,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FFFF00",
                            "n_obj_map_text": "General Admission",
                            "t_note": "Back area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 14,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 14,
                                    "n_id_event": "event124",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 15,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 60,
                            "n_obj_map_cord_x": 90,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FF00FF",
                            "n_obj_map_text": "Economy Section",
                            "t_note": "Far back",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 15,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 15,
                                    "n_id_event": "event124",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 16,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 50,
                            "n_obj_map_cord_x": 100,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#00FFFF",
                            "n_obj_map_text": "Budget Section",
                            "t_note": "Side area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 16,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 16,
                                    "n_id_event": "event124",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 17,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 40,
                            "n_obj_map_cord_x": 110,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FFA500",
                            "n_obj_map_text": "Discount Section",
                            "t_note": "Corner area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 17,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 17,
                                    "n_id_event": "event124",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 18,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 30,
                            "n_obj_map_cord_x": 120,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#800080",
                            "n_obj_map_text": "Promo Section",
                            "t_note": "Remote area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 18,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 18,
                                    "n_id_event": "event124",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 19,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 20,
                            "n_obj_map_cord_x": 130,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#008000",
                            "n_obj_map_text": "Student Section",
                            "t_note": "Upper tier",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 19,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 19,
                                    "n_id_event": "event124",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 20,
                            "n_id_map": 102,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 10,
                            "n_obj_map_cord_x": 140,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#000080",
                            "n_obj_map_text": "Economy Plus Section",
                            "t_note": "Nosebleed section",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 20,
                                    "n_id_event": "event124",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 20,
                                    "n_id_event": "event124",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        }
                    ],
                    "t_map_type": "DISCOTECA"
                },
                {
                    "t_map_name": "Outdoor Arena",
                    "t_map_event_id": "event125",
                    "t_map_id": 103,
                    "t_map_total_seat": 20,
                    "t_map_num_rows":5,
                    "t_map_num_column":4,
                    "t_object_maps": [
                        {
                            "n_id": 21,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 120,
                            "n_obj_map_cord_x": 50,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FF0000",
                            "n_obj_map_text": "VIP Section",
                            "t_note": "Closest to the stage",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 21,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 21,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 22,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 100,
                            "n_obj_map_cord_x": 60,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#00FF00",
                            "n_obj_map_text": "Premium Section",
                            "t_note": "Near the stage",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 22,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 22,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 23,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 90,
                            "n_obj_map_cord_x": 70,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#0000FF",
                            "n_obj_map_text": "Regular Section",
                            "t_note": "Middle area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 23,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 23,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 24,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 80,
                            "n_obj_map_cord_x": 80,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FFFF00",
                            "n_obj_map_text": "General Admission",
                            "t_note": "Back area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 24,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 24,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 25,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 70,
                            "n_obj_map_cord_x": 90,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FF00FF",
                            "n_obj_map_text": "Economy Section",
                            "t_note": "Far back",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 25,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 25,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 26,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 60,
                            "n_obj_map_cord_x": 100,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#00FFFF",
                            "n_obj_map_text": "Budget Section",
                            "t_note": "Side area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 26,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 26,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 27,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 50,
                            "n_obj_map_cord_x": 110,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#FFA500",
                            "n_obj_map_text": "Discount Section",
                            "t_note": "Corner area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 27,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 27,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 28,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 40,
                            "n_obj_map_cord_x": 120,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#800080",
                            "n_obj_map_text": "Promo Section",
                            "t_note": "Remote area",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 28,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 28,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 29,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 30,
                            "n_obj_map_cord_x": 130,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#008000",
                            "n_obj_map_text": "Student Section",
                            "t_note": "Upper tier",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 29,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 29,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        },
                        {
                            "n_id": 30,
                            "n_id_map": 103,
                            "n_min_num_person": 1,
                            "n_max_num_person": 4,
                            "n_limit_buy_for_person": 4,
                            "n_object_price": 20,
                            "n_obj_map_cord_x": 140,
                            "n_obj_map_cord_y": 75,
                            "n_obj_map_cord_z": 0,
                            "n_obj_map_width": 100,
                            "n_obj_map_height": 50,
                            "n_obj_map_fill": "#000080",
                            "n_obj_map_text": "Economy Plus Section",
                            "t_note": "Nosebleed section",
                            "t_type": {
                                "TABLE": {
                                    "DISCOTECA": True
                                }
                            },
                            "is_acquistabile": True,
                            "t_seat_list": [
                                {
                                    "n_seat_num": 1,
                                    "n_object_map_id": 30,
                                    "n_id_event": "event125",
                                    "is_sell": False,
                                    "is_acquistabile": True
                                },
                                {
                                    "n_seat_num": 2,
                                    "n_object_map_id": 30,
                                    "n_id_event": "event125",
                                    "is_sell": True,
                                    "is_acquistabile": False
                                }
                            ]
                        }
                    ],
                    "t_map_type": "DISCOTECA"
                }
            ]#None
            reviews = [
                {
                    "id": "review1",
                    "event_id": "event123",
                    "n_stars": 4.5,
                    "t_title": "Amazing Festival",
                    "t_body": "Had a great time, the music was fantastic!",
                    "t_user": {
                        "t_name": "John",
                        "t_surname": "Doe",
                        "t_alias_generated": "john_doe_123",
                        "t_type": "regular",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg"
                    },
                    "review_date": "2024-08-16T10:00:00.000Z"
                }
            ], #None
            location = {
                "id": "location1",
                "t_address": "123 Festival Lane",
                "t_cap": "12345",
                "t_city": "Music City",
                "t_province": "Music Province",
                "t_state": "Music State",
                "t_location_name": "Music Park"
            } #None
            
            event_list = [
                {
                    "id": "sadasdas123sd",
                    "t_caption": "Evento 1",
                    "t_image_link": "/assets/img/topic-image-placeholder.jpg",
                    "t_user": {
                        "id": 456,
                        "t_name": "Name 1",
                        "t_follower_number": 1705,
                        "t_alias_generated": "Alias1",
                        "t_description": "Ti aiutiamo a diventare la versione migliore di TE STESSO! Seguici su Instagram.",
                        "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                        "t_type": 1,
                        "is_verified": False,
                        "type": "Utenti"
                    },
                    "n_click": 6720272,
                    "type": "Eventi",
                    "created_date": "2024-07-27T15:34:10.111Z",
                    "numOfComment": random.randint(1, 10000),  #count_records("Discussion",{"content_id":content_id}),
                    "numOfLike": random.randint(1, 10000),  #count_records("Like",{"content_id":content_id}),
                    "numOfBooked": random.randint(1, 10000),  #count_records("Booked",{"content_id":content_id})
                    "n_group_id": 1 if random.random() > 0.5 else None,
                    "t_event_date": "2024-07-27T15:34:10.111Z",
                    "t_map_list": maps,
                    "t_reviews": reviews,
                    "t_location": location,
                    "b_active": True,
                    "t_privacy": "Tutti"
                },
                {
                    "id": "sadasdas123sd33sdas",
                    "t_caption": "Evento 2",
                    "t_image_link": "/assets/img/topic-image-placeholder.jpg",
                    "t_user": {
                        "id": 456,
                        "t_name": "Name 1",
                        "t_follower_number": 1705,
                        "t_alias_generated": "Alias1",
                        "t_description": "Ti aiutiamo a diventare la versione migliore di TE STESSO! Seguici su Instagram.",
                        "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                        "t_type": 1,
                        "is_verified": False,
                        "type": "Utenti"
                    },
                    "n_click": 6720272,
                    "type": "Eventi",
                    "created_date": "2024-07-27T15:34:10.111Z",
                    "numOfComment": random.randint(1, 10000),  #count_records("Discussion",{"content_id":content_id}),
                    "numOfLike": random.randint(1, 10000),  #count_records("Like",{"content_id":content_id}),
                    "numOfBooked": random.randint(1, 10000),  #count_records("Booked",{"content_id":content_id})
                    "n_group_id": 1 if random.random() > 0.5 else None,
                    "t_event_date": "2024-07-27T15:34:10.111Z",
                    "t_map_list": maps,
                    "t_reviews": reviews,
                    "t_location": location,
                    "b_active": True,
                    "t_privacy": "Tutti"
                },
                {
                    "id": "sadasdas1asdasd23sd",
                    "t_caption": "Evento 3",
                    "t_image_link": "/assets/img/topic-image-placeholder.jpg",
                    "t_user": {
                        "id": 456,
                        "t_name": "Name 1",
                        "t_follower_number": 1705,
                        "t_alias_generated": "Alias1",
                        "t_description": "Ti aiutiamo a diventare la versione migliore di TE STESSO! Seguici su Instagram.",
                        "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                        "t_type": 1,
                        "is_verified": False,
                        "type": "Utenti"
                    },
                    "n_click": 6720272,
                    "type": "Eventi",
                    "created_date": "2024-07-27T15:34:10.111Z",
                    "numOfComment": random.randint(1, 10000),  #count_records("Discussion",{"content_id":content_id}),
                    "numOfLike": random.randint(1, 10000),  #count_records("Like",{"content_id":content_id}),
                    "numOfBooked": random.randint(1, 10000),  #count_records("Booked",{"content_id":content_id})
                    "n_group_id": 1 if random.random() > 0.5 else None,
                    "t_event_date": "2024-07-27T15:34:10.111Z",
                    "t_map_list": maps,
                    "t_reviews": reviews,
                    "t_location": location,
                    "b_active": True,
                    "t_privacy": "Tutti"
                },
                {
                    "id": "sadasdaxcczxcasds123sd",
                    "t_caption": "Evento 4",
                    "t_image_link": "/assets/img/topic-image-placeholder.jpg",
                    "t_user": {
                        "id": 456,
                        "t_name": "Name 1",
                        "t_follower_number": 1705,
                        "t_alias_generated": "Alias1",
                        "t_description": "Ti aiutiamo a diventare la versione migliore di TE STESSO! Seguici su Instagram.",
                        "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                        "t_type": 1,
                        "is_verified": False,
                        "type": "Utenti"
                    },
                    "n_click": 6720272,
                    "type": "Eventi",
                    "created_date": "2024-07-27T15:34:10.111Z",
                    "numOfComment": random.randint(1, 10000),  #count_records("Discussion",{"content_id":content_id}),
                    "numOfLike": random.randint(1, 10000),  #count_records("Like",{"content_id":content_id}),
                    "numOfBooked": random.randint(1, 10000),  #count_records("Booked",{"content_id":content_id})
                    "n_group_id": 1 if random.random() > 0.5 else None,
                    "t_event_date": "2024-07-27T15:34:10.111Z",
                    "t_map_list": maps,
                    "t_reviews": reviews,
                    "t_location": location,
                    "b_active": True,
                    "t_privacy": "Tutti"
                }
            ]

            if event_list:
                # Costruisci il corpo della risposta come oggetto JSON
                response_body = json.dumps({"events": event_list})

                return func.HttpResponse(
                    body=response_body,
                    status_code=200,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    status_code=404
                )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero delle informazioni utente.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            status_code=404
        )
