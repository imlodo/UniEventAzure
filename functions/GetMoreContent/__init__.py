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
content_collection = db.Contents
# Seleziona la collezione USERS
users_collection = db.Users
# Seleziona la collezione CONTENT_BOOKED
content_like_collection = db.ContentLike

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
        collection = db.ContentBooked
        count = collection.count_documents(filter_params)

    elif countType == 'Discussion':
        collection = db.ContentDiscussion
        count = collection.count_documents(filter_params)

    elif countType == 'Like':
        collection = db.ContentLike
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

    contentType = "ALL"
    match t_more_content_type:
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

    contents = []
    sort_order = pymongo.ASCENDING if order_direction == "ASC" else pymongo.DESCENDING

    if t_more_content_type:
        if contentType == "ALL":
            contents = content_collection.find(query).sort(order_by, sort_order).skip(
                (pageNumber - 1) * pageSize).limit(
                pageSize)
        elif contentType == "EVENTS":
            query["t_type"] = "Eventi"
            contents = content_collection.find(query).sort(order_by, sort_order).skip(
                (pageNumber - 1) * pageSize).limit(
                pageSize)
        elif contentType == "TOPICS":
            query["t_type"] = "Topics"
            contents = content_collection.find(query).sort(order_by, sort_order).skip(
                (pageNumber - 1) * pageSize).limit(
                pageSize)
        elif contentType == "ARTIST":
            query["t_type"] = "ARTIST"
            contents = users_collection.find(query).sort(order_by, sort_order).skip((pageNumber - 1) * pageSize).limit(
                pageSize)
        elif contentType == "USERS":
            query["t_type"] = {"$ne": "ARTIST"}
            contents = users_collection.find(query).sort(order_by, sort_order).skip((pageNumber - 1) * pageSize).limit(
                pageSize)

    content_list = []
    if contentType != "ARTIST" and contentType != "USERS":
        for content in contents:
            is_liked_by_current_user = False
            if user:
                liked_record = content_like_collection.find_one(
                    {"content_id": content["_id"], "t_username": user.get('t_username')})
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
    else:
        return contents


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
            content_list = get_more_content(t_search_str, t_alias_generated, t_more_content_type, order_by,
                                            order_direction, pageNumber, pageSize)

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
