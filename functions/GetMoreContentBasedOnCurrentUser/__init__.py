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
content_collection = db.Content
users_collection = db.User
content_like_collection = db.CONTENT_LIKE
content_booked_collection = db.CONTENT_BOOKED
content_discussion_collection = db.CONTENT_DISCUSSION

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def calculate_user_preferences(t_username):
    user_preferences = Counter()

    # Conteggia i like dell'utente
    likes = content_like_collection.find({"t_username": t_username})
    for like in likes:
        content = content_collection.find_one({"_id": like["content_id"]})
        if content:
            user_preferences.update(content.get("hashtags", []))

    # Conteggia i contenuti preferiti dall'utente
    bookings = content_booked_collection.find({"t_username": t_username})
    for booking in bookings:
        content = content_collection.find_one({"_id": booking["content_id"]})
        if content:
            user_preferences.update(content.get("hashtags", []))

    # Conteggia i commenti dell'utente
    discussions = content_discussion_collection.find({"t_username": t_username})
    for discussion in discussions:
        content = content_collection.find_one({"_id": discussion["content_id"]})
        if content:
            user_preferences.update(content.get("hashtags", []))

    return user_preferences


def get_recommended_content(user_preferences, order_by, order_direction, pageNumber, pageSize):
    query = {"hashtags": {"$in": list(user_preferences.keys())}}
    sort_order = pymongo.ASCENDING if order_direction == "ASC" else pymongo.DESCENDING

    contents = content_collection.find(query).sort(order_by, sort_order).skip((pageNumber - 1) * pageSize).limit(
        pageSize)

    content_list = []
    for content in contents:
        content["preference_score"] = sum(user_preferences.get(tag, 0) for tag in content.get("hashtags", []))
        if '_id' in content:
            del content['_id']
        content_list.append(content)

    content_list.sort(key=lambda x: x["preference_score"], reverse=True)

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
        "is_liked_by_current_user": True if random.randint(0, 1) else False
    }


# Funzione per generare un topic casuale
def generate_random_topics(index):
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
        "is_liked_by_current_user": True if random.randint(0, 1) else False
    }


def load_more_items(count):
    items = []

    for index in range(count):
        if random.random() > 0.5:
            items.append(generate_random_event(index))
        else:
            items.append(generate_random_topics(index))
    return items


# FINE MOCK

def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
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

            req_body = req.get_json()
            order_by = req_body.get('order_by', 'created_date')
            order_direction = req_body.get('order_direction', 'DESC')
            pageNumber = req_body.get('pageNumber', 1)
            pageSize = req_body.get('pageSize', 10)

            # user_preferences = calculate_user_preferences(t_username)
            # content_list = get_recommended_content(user_preferences, order_by, order_direction, pageNumber, pageSize)

            content_list = load_more_items(pageSize)
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
