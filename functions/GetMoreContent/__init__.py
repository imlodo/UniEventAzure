import logging
import os
import pymongo
import jwt
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

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Funzione per ottenere i contenuti in base ai parametri forniti (VA ADATTATA AI VARI T_MORE_CONTENT_TYPE)
def get_more_content(t_search_str, t_alias_generated, t_more_content_type, order_by, order_direction, pageNumber,
                     pageSize):
    query = {}

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
        "event_last_date": generate_random_next_today_date().isoformat()
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
        "created_date": generate_random_date().isoformat()
    }


# Funzione per generare contenuti casuali in base al tipo
def load_more_items(content_type, count):
    items = []
    contentType = "ALL"
    match content_type:
        case "PROFILE_CONTENT" | "PROFILE_BOOKED" | "PROFILE_LIKED" | "EXPLORE_FEATURED" | "EXPLORE_ALL":
            contentType = "ALL"
        case "EXPLORE_EVENTS":
            contentType = "EVENTS"
        case "EXPLORE_TOPICS":
            contentType = "TOPICS"

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
