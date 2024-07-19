import logging
import os
import pymongo
import jwt
import azure.functions as func
from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient
import json

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)
db = client.unieventmongodb
content_collection = db.Contents
location_collection = db.EventLocation
maps_collections = db.EventMaps
object_maps_collections = db.ObjectMaps
object_seats_collections = db.ObjectSeats
content_tags_collections = db.ContentTags
content_mentions_collections = db.ContentMentions

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def store_event_location(t_location, event_id):
    location_data = {
        "event_id": event_id,
        "t_address": t_location.t_address,
        "t_cap": t_location.t_cap,
        "t_city": t_location.t_city,
        "t_location_name": t_location.t_location_name,
        "t_province": t_location.t_province,
        "t_state": t_location.t_state
    }
    return location_collection.insert_one(location_data)


def store_event_maps(t_maps, event_id):
    t_map_object_data = {
        "t_map_name": t_maps.t_map_name,
        "t_map_event_id": event_id,
        "t_map_type": t_maps.t_map_object.t_map_type,
        "t_map_num_column": t_maps.t_map_object.t_map_num_column,
        "t_map_num_rows": t_maps.t_map_object.t_map_num_rows,
        "t_map_total_seat": t_maps.t_map_object.t_map_num_column * t_maps.t_map_object.t_map_num_rows
    }
    mapResult = maps_collections.insert_one(t_map_object_data)

    count = 0
    for obj in t_maps.t_map_object.t_object_maps:
        t_object_map = {
            "n_id_map": mapResult.inserted_id,
            "n_min_num_person": obj.n_min_num_person,
            "n_max_num_person": obj.n_max_num_person,
            "n_limit_buy_for_person": 1,
            "n_object_price": obj.n_object_price,
            "n_obj_map_cord_x": obj.n_obj_map_cord_x,
            "n_obj_map_cord_y": obj.n_obj_map_cord_y,
            "n_obj_map_cord_z": 1,
            "n_obj_map_width": obj.n_obj_map_width,
            "n_obj_map_height": obj.n_obj_map_height,
            "n_obj_map_text": obj.n_obj_map_text,
            "t_type": obj.t_type,
            "is_acquistabile": obj.is_acquistabile
        }

        if obj.n_obj_map_fill:
            t_object_map.update({
                "n_obj_map_fill": obj.n_obj_map_fill
            })

        if obj.t_note:
            t_object_map.update({
                "t_note": obj.t_note
            })

        objectMapResult = object_maps_collections.insert_one(t_object_map)
        count += 1
        countSeat = 0
        for seat in obj.t_seat_list:
            seat_object = {
                "n_seat_num": seat.n_seat_num,
                "n_object_map_id": objectMapResult.inserted_id,
                "n_id_event": event_id,
                "is_sell": False,
                "is_acquistabile": objectMapResult[objectMapResult.inserted_id].is_acquistabile
            }
            object_seats_collections.insert_one(seat_object)
            countSeat += 1


def store_content_tags(tagsArray, content_id):
    for tag in tagsArray:
        tagObj = {
            "value": tag,
            "content_id": content_id
        }
        content_tags_collections.insert_one(tagObj)


def store_content_mentions(mentionsArray, content_id):
    for mention in mentionsArray:
        mentionObj = {
            "value": mention,
            "content_id": content_id
        }
        content_mentions_collections.insert_one(mentionObj)

def get_next_available_group_id():
    # Trova tutti i documenti con un valore n_group_id
    pipeline = [
        {"$match": {"n_group_id": {"$exists": True}}},
        {"$group": {"_id": None, "max_group_id": {"$max": "$n_group_id"}}}
    ]
    result = list(content_collection.aggregate(pipeline))
    if result and result[0].get("max_group_id") is not None:
        return result[0]["max_group_id"] + 1
    else:
        return 1

def get_or_assign_group_event_id(related_event_id):
    content = content_collection.find_one({"_id": ObjectId(related_event_id)})
    if content:
        if "n_group_id" in content:
            return content["n_group_id"]
        else:
            next_group_id = get_next_available_group_id()
            content_collection.update_one(
                {"_id": ObjectId(related_event_id)},
                {"$set": {"n_group_id": next_group_id}}
            )
            return next_group_id
    return None

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

            req_body = req.get_json()

            t_type = req_body.get('t_type')
            t_caption = req_body.get('t_caption')
            t_privacy = req_body.get('t_privacy')
            t_alias_generated = req_body.get('t_alias_generated')
            t_image_link = req_body.get('t_image_link')
            t_video_link = req_body.get('t_video_link', None)
            tagArray = req_body.get('tagArray', [])
            hashTagArray = req_body.get('hashTagArray', [])
            t_event_date = req_body.get('t_event_date', None)
            related_event_id = req_body.get("related_event", None)
            group_event_id = req_body.get('group_event_id', None)
            t_location = req_body.get('t_location', None)
            t_maps = req_body.get('t_maps', None)

            if not (t_type and t_caption and t_privacy and t_alias_generated and t_image_link):
                return func.HttpResponse(
                    "Parametri mancanti nel corpo della richiesta.",
                    status_code=400
                )
            
            if not group_event_id and related_event_id:
                group_event_id = get_or_assign_group_event_id(related_event_id)

            content_data = {
                "t_type": t_type,
                "t_caption": t_caption,
                "t_privacy": t_privacy,
                "t_alias_generated": t_alias_generated,
                "t_image_link": t_image_link,
                "t_video_link": t_video_link,
                "b_active": True,
                "n_click": 0,
                "created_date": datetime.utcnow().isoformat(),
            }

            if t_type.lower() == "eventi":
                if not (t_event_date and t_location and t_maps):
                    return func.HttpResponse(
                        "Parametri mancanti per l'evento nel corpo della richiesta.",
                        status_code=400
                    )
                content_data.update({
                    "t_event_date": t_event_date,
                    "group_event_id": group_event_id
                })

            # result = content_collection.insert_one(content_data)
            # content_data['id'] = str(result.inserted_id)

            # if t_type.lower() == "eventi":
            #     locationResult = store_event_location(t_location, content_data['id'])
            #     content_data['location'] = locationResult
            #     store_event_maps(t_maps, content_data['id'])

            # if hashTagArray:
            #     store_content_tags(hashTagArray, content_data['id'])

            # if tagArray: 
            #     store_content_mentions(tagArray, content_data['id'])

            return func.HttpResponse(
                body=json.dumps(content_data),
                status_code=201,
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
