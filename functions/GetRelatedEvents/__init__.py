import logging
import os
import json
from datetime import datetime

import jwt
from dotenv import load_dotenv
from pymongo import MongoClient
import azure.functions as func

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Ottieni la stringa di connessione dal file delle variabili d'ambiente
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    "Autorizzazione non valida.",
                    status_code=401
                )

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')
            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse("Token scaduto.", status_code=401)
            except jwt.InvalidTokenError:
                return func.HttpResponse("Token non valido.", status_code=401)

            # Ottieni l'username dal token decodificato
            username = decoded_token.get('username')
            if not username:
                return func.HttpResponse("Token non contiene un username valido.", status_code=401)

            # Ottieni il parametro n_group_id dalla query string
            n_group_id = req.params.get('n_group_id')
            if not n_group_id:
                return func.HttpResponse("n_group_id è richiesto.", status_code=400)

            # # Recupera gli eventi dal database
            # events = db.Content.find({"n_group_id": int(n_group_id)})
            # 
            # event_details = []
            # for event in events:
            #     event_id = event.get("id")
            #     t_alias_generated = event.get("t_user").get("t_alias_generated")
            # 
            #     # Recupera l'utente
            #     user = db.USERS.find_one({"t_alias_generated": t_alias_generated})
            # 
            #     # Recupera le mappe
            #     maps = list(db.EventMaps.find({"t_map_event_id": event_id}))
            #     for map_item in maps:
            #         t_map_id = map_item.get("t_map_id")
            # 
            #         # Recupera gli oggetti della mappa
            #         object_maps = list(db.ObjectMaps.find({"n_id_map": t_map_id}))
            #         map_item["t_object_maps"] = object_maps
            # 
            #     # Recupera le recensioni
            #     reviews = list(db.TicketReviews.find({"event_id": event_id}))
            # 
            #     # Recupera la location
            #     location = db.EventLocation.find_one({"event_id": event_id})
            # 
            #     # Costruisci l'oggetto EventDetail
            #     event_detail = {
            #         "id": event_id,
            #         "n_group_id": event.get("n_group_id"),
            #         "n_click": event.get("n_click"),
            #         "t_caption": event.get("t_caption"),
            #         "t_image_link": event.get("t_image_link"),
            #         "t_event_date": event.get("t_event_date"),
            #         "t_map_list": maps,
            #         "t_reviews": reviews,
            #         "t_user": user,
            #         "t_location": location,
            #         "b_active": event.get("b_active"),
            #         "t_privacy": event.get("t_privacy")
            #     }
            # 
            #     event_details.append(event_detail)

            event_details = [
                {
                    "id": "event123",
                    "n_group_id": 1,
                    "n_click": 42,
                    "t_caption": "Summer Music Festival",
                    "t_image_link": "https://rivieraticket.it/wp-content/uploads/2023/08/Tropical-closing-party-Byblos-01-09-23.jpg",
                    "t_event_date": "2024-08-15T19:00:00.000Z",
                    "t_map_list": [
                        {
                            "t_map_name": "Main Stage",
                            "t_map_event_id": "event123",
                            "t_map_id": 101,
                            "t_map_total_seat": 5000,
                            "t_object_maps": [
                                {
                                    "n_id": 1,
                                    "n_id_map": 101,
                                    "n_min_num_person": 1,
                                    "n_max_num_person": 4,
                                    "n_limit_buy_for_person": 4,
                                    "n_object_price": 100,
                                    "n_obj_map_cord_x": 50,
                                    "n_obj_map_cord_y": 75,
                                    "n_obj_map_cord_z": 0,
                                    "n_obj_map_width": 10,
                                    "n_obj_map_height": 10,
                                    "n_obj_map_fill": "#FF0000",
                                    "n_obj_map_text": "VIP Section",
                                    "t_note": "Closest to the stage",
                                    "t_type": {
                                        "TABLE": {
                                            "DISCOTECA": False
                                        }
                                    },
                                    "is_acquistabile": True,
                                    "t_seat_list": [
                                        {
                                            "n_seat_num": 1,
                                            "n_object_map_id": 1,
                                            "n_id_event": "event123",
                                            "is_sell": False,
                                            "is_acquistabile": True
                                        },
                                        {
                                            "n_seat_num": 2,
                                            "n_object_map_id": 1,
                                            "n_id_event": "event123",
                                            "is_sell": True,
                                            "is_acquistabile": False
                                        }
                                    ]
                                }
                            ],
                            "t_map_type": "DISCOTECA"
                        }
                    ],
                    "t_reviews": [
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
                    ],
                    "t_user": {
                        "t_name": "Alice",
                        "t_surname": "Smith",
                        "t_alias_generated": "alice_smith_456",
                        "t_type": "organizer",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg"
                    },
                    "t_location": {
                        "id": "location1",
                        "t_address": "123 Festival Lane",
                        "t_cap": "12345",
                        "t_city": "Music City",
                        "t_province": "Music Province",
                        "t_state": "Music State",
                        "t_location_name": "Music Park"
                    },
                    "b_active": True,
                    "t_privacy": "All"
                },
                {
                    "id": "event124",
                    "n_group_id": 1,
                    "n_click": 25,
                    "t_caption": "Tech Conference",
                    "t_image_link": "https://rivieraticket.it/wp-content/uploads/2023/08/Tropical-closing-party-Byblos-01-09-23.jpg",
                    "t_event_date": "2024-09-20T09:00:00.000Z",
                    "t_map_list": [
                        {
                            "t_map_name": "Main Hall",
                            "t_map_event_id": "event124",
                            "t_map_id": 102,
                            "t_map_total_seat": 2000,
                            "t_object_maps": [
                                {
                                    "n_id": 2,
                                    "n_id_map": 102,
                                    "n_min_num_person": 1,
                                    "n_max_num_person": 10,
                                    "n_limit_buy_for_person": 10,
                                    "n_object_price": 150,
                                    "n_obj_map_cord_x": 30,
                                    "n_obj_map_cord_y": 60,
                                    "n_obj_map_cord_z": 0,
                                    "n_obj_map_width": 20,
                                    "n_obj_map_height": 20,
                                    "n_obj_map_fill": "#00FF00",
                                    "n_obj_map_text": "Premium Section",
                                    "t_note": "Best view of the stage",
                                    "t_type": {
                                        "TABLE": {
                                            "DISCOTECA": False
                                        }
                                    },
                                    "is_acquistabile": True,
                                    "t_seat_list": [
                                        {
                                            "n_seat_num": 1,
                                            "n_object_map_id": 2,
                                            "n_id_event": "event124",
                                            "is_sell": False,
                                            "is_acquistabile": True
                                        },
                                        {
                                            "n_seat_num": 2,
                                            "n_object_map_id": 2,
                                            "n_id_event": "event124",
                                            "is_sell": True,
                                            "is_acquistabile": False
                                        }
                                    ]
                                }
                            ],
                            "t_map_type": "CONFERENCE"
                        }
                    ],
                    "t_reviews": [
                        {
                            "id": "review2",
                            "event_id": "event124",
                            "n_stars": 5,
                            "t_title": "Incredibly Informative",
                            "t_body": "Learned so much, great speakers!",
                            "t_user": {
                                "t_name": "Jane",
                                "t_surname": "Doe",
                                "t_alias_generated": "jane_doe_789",
                                "t_type": "regular",
                                "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg"
                            },
                            "review_date": "2024-09-21T11:00:00.000Z"
                        }
                    ],
                    "t_user": {
                        "t_name": "Bob",
                        "t_surname": "Johnson",
                        "t_alias_generated": "bob_johnson_101",
                        "t_type": "organizer",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg"
                    },
                    "t_location": {
                        "id": "location2",
                        "t_address": "456 Tech Avenue",
                        "t_cap": "67890",
                        "t_city": "Tech City",
                        "t_province": "Tech Province",
                        "t_state": "Tech State",
                        "t_location_name": "Tech Center"
                    },
                    "b_active": True,
                    "t_privacy": "All"
                }
            ]
            return func.HttpResponse(
                body=json.dumps(event_details),
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero dei dettagli degli eventi.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo GET.",
            status_code=405
        )
