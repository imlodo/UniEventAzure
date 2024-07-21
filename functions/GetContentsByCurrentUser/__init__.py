import logging
import os
import random
from collections import Counter
from datetime import datetime, timedelta

import pymongo
from azure.functions import HttpResponse
from pymongo import MongoClient
import azure.functions as func
import json
import jwt

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
content_collection = db.Contents
users_collection = db.Users
content_like_collection = db.ContentLike
content_booked_collection = db.ContentBooked
content_discussion_collection = db.ContentDiscussion

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def get_content_by_current_user(t_alias_generated):
    content_list = content_collection.find({"t_alias_generated": t_alias_generated})

    return content_list


#MOCK
# Didascalie di esempio
didascalie = [
    'Evento emozionante', 'Esperienza indimenticabile', 'Avventura entusiasmante', 'Momenti avvincenti',
    'Una serata da ricordare', 'Raduno magico', 'Spettacolo spettacolare', 'Celebrazione della comunità',
    'Simposio ispiratore', 'Estravaganza culturale', 'Performance mozzafiato', 'Vetrina artistica',
    'Laboratorio interattivo', 'Concerto epico', 'Forum educativo', 'Festività all\'aperto',
    'Mostra innovativa', 'Simposio creativo', 'Esposizione divertente', 'Occasione speciale',
    'Conferenza dinamica', 'Incontro sociale', 'Esperienza di realtà virtuale', 'Presentazione unica',
    'Vertice tecnologico', 'Estravaganza di moda', 'Ritiro benessere', 'Scoperta di nuovi orizzonti',
    'Viaggio musicale', 'Vetrina artigianale', 'Evento di networking globale', 'Intrattenimento sbalorditivo',
    'Seminario impattante', 'Festival gastronomico', 'Iniziativa eco-friendly', 'Delizie epicuree',
    'Esplorazione di nuovi fronti', 'Campionamento del cambiamento', 'Performance teatrale', 'Gemme nascoste rivelate',
    'Celebrare la diversità', 'Avventura gastronomica', 'Simposio futuristico', 'Delizie culinarie',
    'Esperienza interattiva', 'Idee rivoluzionarie', 'Sotto i riflettori dei talenti emergenti'
]

# Utente di esempio
user = {
    "_id": "012933923",
    "t_username": "johndoe",
    "t_password": "hashed_password",
    "t_name": "John",
    "t_surname": "Doe",
    "t_alias_generated": "JD",
    "t_description": "Lorem ipsum dolor sit amet.",
    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
    "is_verified": False,
    "t_type": "CREATOR"
}


def random_int_from_interval(min_val, max_val):
    return random.randint(min_val, max_val)


# Funzione per generare una data casuale
def generate_random_date():
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    return start_date + (end_date - start_date) * random.random()


# Funzione per generare una data casuale futura
def generate_random_next_today_date():
    return datetime.now() + timedelta(days=random_int_from_interval(1, 30))


def generate_random_event(index):
    random_int_value = random_int_from_interval(0, 1)
    randomEl = random.random()
    return {
        "id": index,
        "t_caption": random.choice(didascalie),
        "t_image_link": '/assets/img/exampleEventFirstFrame.png' if random_int_value == 0 else '/assets/img/event-image-placeholder.jpg',
        "t_video_link": '/assets/videos/exampleEventVideo.mp4' if random_int_value == 0 else None,
        "t_event_date": datetime.now().isoformat(),
        "t_user": user,
        "n_click": random_int_from_interval(1, 10000000),
        "type": "Eventi",
        "created_date": generate_random_date().isoformat(),
        "event_first_date": generate_random_next_today_date().isoformat(),
        "event_last_date": generate_random_next_today_date().isoformat(),
        "numOfComment": random.randint(1, 10000),
        "numOfLike": random.randint(1, 10000),
        "numOfBooked": random.randint(1, 10000),
        "is_liked_by_current_user": True if random.randint(0, 1) else False,
        "t_privacy": "all" if randomEl < 0.4 else "amici" if 0.4 < randomEl < 0.7 else "onlyu"
    }


# Funzione per generare un topic casuale
def generate_random_topics(index):
    randomEl = random.random()
    random_int_value = random_int_from_interval(0, 1)
    return {
        "id": index,
        "t_caption": random.choice(didascalie),
        "t_image_link": '/assets/img/exampleTopicImageFristFrame.png' if random_int_value == 0 else '/assets/img/topic-image-placeholder.jpg',
        "t_video_link": '/assets/videos/exampleTopicsVideo.mp4' if random_int_value == 0 else None,
        "t_topic_date": datetime.now().isoformat(),
        "t_user": user,
        "n_click": random_int_from_interval(1, 10000000),
        "type": "Topics",
        "created_date": generate_random_date().isoformat(),
        "numOfComment": random.randint(1, 10000),
        "numOfLike": random.randint(1, 10000),
        "numOfBooked": random.randint(1, 10000),
        "is_liked_by_current_user": True if random.randint(0, 1) else False,
        "t_privacy": "all" if randomEl < 0.4 else "amici" if 0.4 < randomEl < 0.7 else "onlyu"
    }


# FINE MOCK

def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
        try:
            token = req.headers.get('Authorization')
            if not token:
                return HttpResponse("Token mancante.", status_code=401)

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
            # userRetrived = users_collection.find_one({"t_username": t_username})
            # content_list = get_content_by_current_user(userRetrived.get("t_alias_generated"))
            
            content_list = [
                generate_random_event(1),
                generate_random_topics(2),
                generate_random_event(3),
                generate_random_topics(4),
                generate_random_topics(5)
            ]
            response_body = json.dumps({"content_list": content_list})

            return HttpResponse(
                body=response_body,
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return HttpResponse(
                "Si è verificato un errore durante il recupero dei contenuti.",
                status_code=500
            )

    else:
        return HttpResponse(
            status_code=404
        )
