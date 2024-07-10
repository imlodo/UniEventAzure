import logging
import os
from enum import Enum

import pymongo
from datetime import datetime, timedelta
from azure.functions import HttpResponse
from pymongo import MongoClient
import azure.functions as func
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
content_collection = db.Content
# Seleziona la collezione USERS
users_collection = db.User
# Seleziona la collezione CONTENT_BOOKED
content_like_collection = db.CONTENT_LIKE

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def count_records(countType, params):
    if 'content_id' not in params:
        raise ValueError("Il parametro content_id è obbligatorio.")
    else:
        filter_params = {
            'content_id': str(params['content_id']),
        }

    if countType == 'Booked':
        collection = db.CONTENT_BOOKED
        count = collection.count_documents(filter_params)

    elif countType == 'Discussion':
        collection = db.CONTENT_DISCUSSION
        count = collection.count_documents(filter_params)

    elif countType == 'Like':
        collection = db.CONTENT_LIKE
        count = collection.count_documents(filter_params)

    else:
        raise ValueError(f"countType '{countType}' non valido.")

    return count

# Funzione per ottenere i contenuti in base ai parametri forniti (VA ADATTATA AI VARI T_MORE_CONTENT_TYPE)
def get_more_content(t_search_str, t_alias_generated, t_more_content_type, order_by, order_direction, pageNumber,
                     pageSize):
    query = {}
    user = users_collection.find_one({"t_alias_generated": t_alias_generated})
    if t_search_str:
        query["t_caption"] = {"$regex": t_search_str, "$options": "i"}

    if t_alias_generated:
        query["t_user.t_alias_generated"] = t_alias_generated

    match t_more_content_type:
        case "PROFILE_CONTENT":
            return
        case "PROFILE_BOOKED":
            return
        case "PROFILE_LIKED":
            return
        case "EXPLORE_FEATURED":
            return
        case "EXPLORE_FOLLOWED":
            return
        case "EXPLORE_EVENTS":
            return
        case "EXPLORE_TOPICS":
            return
        case "EXPLORE_ALL":
            return

    if t_more_content_type:
        query["type"] = t_more_content_type

    sort_order = pymongo.ASCENDING if order_direction == "ASC" else pymongo.DESCENDING

    contents = content_collection.find(query).sort(order_by, sort_order).skip((pageNumber - 1) * pageSize).limit(
        pageSize)

    content_list = []
    for content in contents:
        is_liked_by_current_user = False
        if user:
            liked_record = content_like_collection.find_one({"content_id": content["_id"], "t_username": user.get('t_username')})
            if liked_record:
                is_liked_by_current_user = True
        numOfComment = count_records("Discussion", {"content_id": content["_id"]})
        numOfLike = count_records("Like", {"content_id": content["_id"]})
        numOfBooked = count_records("Booked", {"content_id": content["_id"]})
        content["numOfComment"] = numOfComment
        content["numOfLike"] = numOfLike
        content["numOfBooked"] = numOfBooked
        content["is_liked_by_current_user"] = is_liked_by_current_user
        if '_id' in content:
            del content['_id']
        content_list.append(content)

    return content_list


#################################### MOCK ######################################
import random

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


class USER_TYPE(Enum):
    ARTIST = "ARTIST"
    CREATOR = "CREATOR"
    COMPANY = "COMPANY"


# Funzione per generare un numero casuale tra un intervallo
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


# Funzione per generare un evento casuale
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
        "is_liked_by_current_user": True if random.randint(0,1) else False
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
        "is_liked_by_current_user": True if random.randint(0,1) else False
    }


def generate_random_account(index, user_type):
    randomNumber = random_int_from_interval(1, 3)
    randomAccountType = USER_TYPE.ARTIST if user_type == "Artist" else USER_TYPE.CREATOR if randomNumber == 2 else USER_TYPE.COMPANY
    return {
        "id": index,
        "t_name": "Name" + str(index + 1),
        "t_follower_number": random_int_from_interval(100, 10000),
        "t_alias_generated": "alias" + str(index + 1),
        "t_description": "Ti aiutiamo a diventare la versione migliore di TE STESSO! Seguici su Instagram.",
        "t_profile_photo": '/assets/img/example_artist_image.jpg' if randomAccountType == USER_TYPE.ARTIST else "/assets/img/userExampleImg.jpeg",
        "t_type": randomAccountType.value,
        "is_verified": True if random_int_from_interval(0, 5) > 3 and randomAccountType == USER_TYPE.ARTIST else False,
    }


# Funzione per generare contenuti casuali in base al tipo
def load_more_items(content_type, count):
    items = []
    contentType = "ALL"
    match content_type:
        case "PROFILE_CONTENT" | "PROFILE_BOOKED" | "PROFILE_LIKED" | "EXPLORE_FEATURED" | "EXPLORE_ALL" | "SEARCH_ALL":
            contentType = "ALL"
        case "EXPLORE_EVENTS" | "SEARCH_EVENTS":
            contentType = "EVENTS"
        case "EXPLORE_TOPICS" | "SEARCH_TOPICS":
            contentType = "TOPICS"
        case "SEARCH_ARTIST":
            contentType = "ARTISTS"
        case "SEARCH_USER":
            contentType = "USERS"

    if contentType == "ALL":
        for index in range(count):
            if random.random() > 0.5:
                items.append(generate_random_event(index))
            else:
                items.append(generate_random_topics(index))
        return items
    elif contentType == "EVENTS":
        for index in range(count):
            items.append(generate_random_event(index))
        return items
    elif contentType == "TOPICS":
        for index in range(count):
            items.append(generate_random_topics(index))
        return items
    elif contentType == "USERS":
        for index in range(count):
            items.append(generate_random_account(index, "USER"))
        return items
    elif contentType == "ARTISTS":
        for index in range(count):
            items.append(generate_random_account(index, "Artist"))
        return items


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        try:
            req_body = req.get_json()
            t_search_str = req_body.get('t_search_str', '')
            t_alias_generated = req_body.get('t_alias_generated', '')
            t_more_content_type = req_body.get('t_more_content_type')
            order_by = req_body.get('order_by', 'created_date')
            order_direction = req_body.get('order_direction', 'DESC')
            pageNumber = req_body.get('pageNumber', 1)
            pageSize = req_body.get('pageSize', 10)

            if not t_more_content_type:
                return HttpResponse(
                    "Parametro t_more_content_type mancante.",
                    status_code=400
                )

            # Ottieni i contenuti dal database in base ai parametri forniti
            # content_list = get_more_content(t_search_str, t_alias_generated, t_more_content_type, order_by,
            #                                 order_direction, pageNumber, pageSize)

            # Mock
            content_list = load_more_items(t_more_content_type, pageSize)
            reverse = (order_direction == 'DESC')
            content_list.sort(key=lambda x: x.get(order_by, datetime.now()), reverse=reverse)
            #fine mock

            # Costruisci il corpo della risposta come oggetto JSON
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