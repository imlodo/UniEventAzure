import logging
import os
import pymongo
import jwt
from datetime import datetime
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
users_collection = db.User
content_collection = db.Contents
content_booked_collection = db.ContentBooked
content_liked_collection = db.ContentLiked
follow_user_collection = db.FollowUser

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Funzione per ottenere i dettagli dell'utente
def get_user_info(t_alias_generated):
    user = users_collection.find_one({"t_alias_generated": t_alias_generated})
    if user:
        if '_id' in user:
            del user['_id']
        if 't_password' in user:
            del user['t_password']
        return user
    return None


# Funzione per ottenere i contenuti dell'utente (ultimi 5)
def get_user_content(t_alias_generated, limit=5):
    contents = content_collection.find({"t_user.t_alias_generated": t_alias_generated}).sort("created_date",
                                                                                             pymongo.DESCENDING).limit(
        limit)
    content_list = []
    for content in contents:
        if '_id' in content:
            del content['_id']
        content_list.append(content)
    return content_list


# Funzione per ottenere i contenuti aggiunti ai preferiti dall'utente (ultimi 5)
def get_user_booked_content(t_alias_generated, limit=5):
    booked_contents = content_booked_collection.find({"t_user.t_alias_generated": t_alias_generated}).sort(
        "created_date", pymongo.DESCENDING).limit(limit)
    content_list = []
    for booked in booked_contents:
        content = content_collection.find_one({"id": booked["content_id"]})
        if content:
            if '_id' in content:
                del content['_id']
            content_list.append(content)
    return content_list


# Funzione per ottenere i contenuti piaciuti dall'utente (ultimi 5)
def get_user_liked_content(t_alias_generated, limit=5):
    liked_contents = content_liked_collection.find({"t_user.t_alias_generated": t_alias_generated}).sort("created_date",
                                                                                                         pymongo.DESCENDING).limit(
        limit)
    content_list = []
    for liked in liked_contents:
        content = content_collection.find_one({"id": liked["content_id"]})
        if content:
            if '_id' in content:
                del content['_id']
            content_list.append(content)
    return content_list


# Funzione per ottenere il conteggio dei likes
def get_count_like(t_alias_generated):
    liked_contents = content_liked_collection.find({"t_user.t_alias_generated": t_alias_generated})
    return liked_contents.count()


# Funzione per ottenere il conteggio dei follower
def get_count_follower(t_alias_generated):
    followers = follow_user_collection.find({"t_username_1": t_alias_generated})
    return followers.count()


# Funzione per ottenere il conteggio delle persone seguite
def get_count_followed(t_alias_generated):
    followed = follow_user_collection.find({"t_username_2": t_alias_generated})
    return followed.count()


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return HttpResponse(status_code=404)

            jwt_token = auth_header.split(' ')[1]

            # Decodifica il token JWT
            secret_key = os.getenv('JWT_SECRET_KEY')
            try:
                jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return HttpResponse(status_code=404)
            except jwt.InvalidTokenError:
                return HttpResponse(status_code=404)

            # Ottieni l'alias dall'URL della richiesta
            t_alias_generated = req.params.get('t_alias_generated')
            if not t_alias_generated:
                return HttpResponse(
                    "Parametro t_alias_generated mancante.",
                    status_code=400
                )

            # Ottieni le informazioni dell'utente dal database
            # user_info = get_user_info(t_alias_generated)
            # if not user_info:
            #     return HttpResponse(status_code=404)

            # Ottieni i contenuti dell'utente dal database (ultimi 5)
            # content_list = get_user_content(t_alias_generated)
            # booked_list = get_user_booked_content(t_alias_generated)
            # liked_list = get_user_liked_content(t_alias_generated)

            content_list = [
                {
                    "id": 123,
                    "t_caption": "Conferenza Dinamica",
                    "t_image_link": "http://localhost:4200/assets/img/topic-image-placeholder.jpg",
                    "t_user": {
                        "_id": "012933923", "t_username": "johndoe", "t_password": "hashed_password",
                        "t_name": "John", "t_surname": "Doe", "t_alias_generated": "JD",
                        "t_description": "Lorem ipsum dolor sit amet.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": False, "t_type": "CREATOR"
                    },
                    "n_click": 4748049,
                    "type": "Topics",
                    "created_date": "2024-06-23T09:55:14.998Z"
                },
                {
                    "id": 144,
                    "t_caption": "Concerto Epico",
                    "t_image_link": "http://localhost:4200/assets/img/exampleEventFirstFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleEventVideo.mp4",
                    "t_event_date": "2024-07-23",
                    "t_user": {
                        "_id": "012933923", "t_username": "johndoe", "t_password": "hashed_password",
                        "t_name": "John", "t_surname": "Doe", "t_alias_generated": "JD",
                        "t_description": "Lorem ipsum dolor sit amet.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": False, "t_type": "CREATOR"
                    },
                    "n_click": 359089,
                    "type": "Eventi",
                    "created_date": "2024-07-23",
                    "event_first_date": "2024-07-23",
                    "event_last_date": "2024-07-26",
                },
                {
                    "id": 146,
                    "t_caption": "Come accedere ad Unisa?",
                    "t_image_link": "http://localhost:4200/assets/img/exampleTopicImageFristFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleTopicsVideo.mp4",
                    "t_user": {
                        "_id": "012933923", "t_username": "johndoe", "t_password": "hashed_password",
                        "t_name": "John", "t_surname": "Doe", "t_alias_generated": "JD",
                        "t_description": "Lorem ipsum dolor sit amet.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": False, "t_type": "CREATOR"
                    },
                    "n_click": 159089,
                    "type": "Topics",
                    "created_date": "2024-07-23",
                },
                {
                    "id": 148,
                    "t_caption": "La black",
                    "t_image_link": "http://localhost:4200/assets/img/exampleEventFirstFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleEventVideo.mp4",
                    "t_event_date": "2024-07-23",
                    "t_user": {
                        "_id": "012933923", "t_username": "johndoe", "t_password": "hashed_password",
                        "t_name": "John", "t_surname": "Doe", "t_alias_generated": "JD",
                        "t_description": "Lorem ipsum dolor sit amet.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": False, "t_type": "CREATOR"
                    },
                    "n_click": 759089,
                    "type": "Eventi",
                    "created_date": "2024-07-23",
                    "event_first_date": "2024-07-23",
                    "event_last_date": "2024-07-26",
                },
                {
                    "id": 152,
                    "t_caption": "La black, il ritorno di mario baldi",
                    "t_image_link": "http://localhost:4200/assets/img/event-image-placeholder.jpg",
                    "t_event_date": "2024-07-23",
                    "t_user": {
                        "_id": "012933923", "t_username": "johndoe", "t_password": "hashed_password",
                        "t_name": "John", "t_surname": "Doe", "t_alias_generated": "JD",
                        "t_description": "Lorem ipsum dolor sit amet.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": False, "t_type": "CREATOR"
                    },
                    "n_click": 359089,
                    "type": "Eventi",
                    "created_date": "2024-07-23",
                    "event_first_date": "2024-07-23",
                    "event_last_date": "2024-07-26",
                }
            ]
            booked_list = [
                {
                    "id": 150,
                    "t_caption": "Tecniche di Pittura",
                    "t_image_link": "http://localhost:4200/assets/img/exampleTopicImageFristFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleTopicsVideo.mp4",
                    "t_user": {
                        "_id": "012933928", "t_username": "artlover", "t_password": "hashed_password",
                        "t_name": "Art", "t_surname": "Lover", "t_alias_generated": "artlover",
                        "t_description": "Amante delle belle arti e della pittura.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": False, "t_type": "CREATOR"
                    },
                    "n_click": 120034,
                    "type": "Topics",
                    "created_date": "2024-08-25",
                },
                {
                    "id": 151,
                    "t_caption": "Incontro con lo Scrittore",
                    "t_image_link": "http://localhost:4200/assets/img/exampleEventFirstFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleEventVideo.mp4",
                    "t_event_date": "2024-09-20",
                    "t_user": {
                        "_id": "012933929", "t_username": "bookworm", "t_password": "hashed_password",
                        "t_name": "Book", "t_surname": "Worm", "t_alias_generated": "bookworm",
                        "t_description": "Avido lettore e critico letterario.",
                        "t_profile_photo": "http://localhost:4200/assets/img/example_artist_image.jpg",
                        "is_verified": False, "t_type": "CREATOR"
                    },
                    "n_click": 230987,
                    "type": "Eventi",
                    "created_date": "2024-09-10",
                    "event_first_date": "2024-09-20",
                    "event_last_date": "2024-09-22",
                },
                {
                    "id": 153,
                    "t_caption": "Lezioni di Chitarra",
                    "t_image_link": "http://localhost:4200/assets/img/exampleTopicImageFristFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleTopicsVideo.mp4",
                    "t_user": {
                        "_id": "012933930", "t_username": "guitarhero", "t_password": "hashed_password",
                        "t_name": "Guitar", "t_surname": "Hero", "t_alias_generated": "guitarhero",
                        "t_description": "Chitarrista esperto e insegnante di musica.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": True, "t_type": "ARTIST"
                    },
                    "n_click": 340000,
                    "type": "Topics",
                    "created_date": "2024-10-01",
                },
                {
                    "id": 144,
                    "t_caption": "Raduno magico",
                    "t_image_link": "http://localhost:4200/assets/img/exampleEventFirstFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleEventVideo.mp4",
                    "t_event_date": "2024-07-23",
                    "t_user": {
                        "_id": "012933924", "t_username": "mariobaldi", "t_password": "hashed_password",
                        "t_name": "Mario", "t_surname": "Baldi", "t_alias_generated": "mariobaldi",
                        "t_description": "Lorem ipsum dolor sit amet.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": True, "t_type": "ARTIST"
                    },
                    "n_click": 359089,
                    "type": "Eventi",
                    "created_date": "2024-07-23",
                    "event_first_date": "2024-07-23",
                    "event_last_date": "2024-07-26",
                },
                {
                    "id": 149,
                    "t_caption": "Festa del Cinema",
                    "t_image_link": "http://localhost:4200/assets/img/exampleEventFirstFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleEventVideo.mp4",
                    "t_event_date": "2024-08-01",
                    "t_user": {
                        "_id": "012933927", "t_username": "cinemafan", "t_password": "hashed_password",
                        "t_name": "Cine", "t_surname": "Fan", "t_alias_generated": "cinemafan",
                        "t_description": "Appassionato di cinema e film d'autore.",
                        "t_profile_photo": "http://localhost:4200/assets/img/example_artist_image.jpg",
                        "is_verified": True, "t_type": "CREATOR"
                    },
                    "n_click": 482000,
                    "type": "Eventi",
                    "created_date": "2024-07-30",
                    "event_first_date": "2024-08-01",
                    "event_last_date": "2024-08-05",
                }
            ]
            liked_list = [
                {
                    "id": 144,
                    "t_caption": "Raduno magico",
                    "t_image_link": "http://localhost:4200/assets/img/exampleEventFirstFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleEventVideo.mp4",
                    "t_event_date": "2024-07-23",
                    "t_user": {
                        "_id": "012933924", "t_username": "mariobaldi", "t_password": "hashed_password",
                        "t_name": "Mario", "t_surname": "Baldi", "t_alias_generated": "mariobaldi",
                        "t_description": "Lorem ipsum dolor sit amet.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": True, "t_type": "ARTIST"
                    },
                    "n_click": 359089,
                    "type": "Eventi",
                    "created_date": "2024-07-23",
                    "event_first_date": "2024-07-23",
                    "event_last_date": "2024-07-26",
                },
                {
                    "id": 149,
                    "t_caption": "Festa del Cinema",
                    "t_image_link": "http://localhost:4200/assets/img/exampleEventFirstFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleEventVideo.mp4",
                    "t_event_date": "2024-08-01",
                    "t_user": {
                        "_id": "012933927", "t_username": "cinemafan", "t_password": "hashed_password",
                        "t_name": "Cine", "t_surname": "Fan", "t_alias_generated": "cinemafan",
                        "t_description": "Appassionato di cinema e film d'autore.",
                        "t_profile_photo": "http://localhost:4200/assets/img/example_artist_image.jpg",
                        "is_verified": True, "t_type": "CREATOR"
                    },
                    "n_click": 482000,
                    "type": "Eventi",
                    "created_date": "2024-07-30",
                    "event_first_date": "2024-08-01",
                    "event_last_date": "2024-08-05",
                },
                {
                    "id": 150,
                    "t_caption": "Tecniche di Pittura",
                    "t_image_link": "http://localhost:4200/assets/img/exampleTopicImageFristFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleTopicsVideo.mp4",
                    "t_user": {
                        "_id": "012933928", "t_username": "artlover", "t_password": "hashed_password",
                        "t_name": "Art", "t_surname": "Lover", "t_alias_generated": "artlover",
                        "t_description": "Amante delle belle arti e della pittura.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": False, "t_type": "CREATOR"
                    },
                    "n_click": 120034,
                    "type": "Topics",
                    "created_date": "2024-08-25",
                },
                {
                    "id": 151,
                    "t_caption": "Incontro con lo Scrittore",
                    "t_image_link": "http://localhost:4200/assets/img/exampleEventFirstFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleEventVideo.mp4",
                    "t_event_date": "2024-09-20",
                    "t_user": {
                        "_id": "012933929", "t_username": "bookworm", "t_password": "hashed_password",
                        "t_name": "Book", "t_surname": "Worm", "t_alias_generated": "bookworm",
                        "t_description": "Avido lettore e critico letterario.",
                        "t_profile_photo": "http://localhost:4200/assets/img/example_artist_image.jpg",
                        "is_verified": False, "t_type": "CREATOR"
                    },
                    "n_click": 230987,
                    "type": "Eventi",
                    "created_date": "2024-09-10",
                    "event_first_date": "2024-09-20",
                    "event_last_date": "2024-09-22",
                },
                {
                    "id": 153,
                    "t_caption": "Lezioni di Chitarra",
                    "t_image_link": "http://localhost:4200/assets/img/exampleTopicImageFristFrame.png",
                    "t_video_link": "http://localhost:4200/assets/videos/exampleTopicsVideo.mp4",
                    "t_user": {
                        "_id": "012933930", "t_username": "guitarhero", "t_password": "hashed_password",
                        "t_name": "Guitar", "t_surname": "Hero", "t_alias_generated": "guitarhero",
                        "t_description": "Chitarrista esperto e insegnante di musica.",
                        "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                        "is_verified": True, "t_type": "ARTIST"
                    },
                    "n_click": 340000,
                    "type": "Topics",
                    "created_date": "2024-10-01",
                }
            ]

            # Ottieni i conteggi
            # count_followed = get_count_followed(t_alias_generated)
            # count_follower = get_count_follower(t_alias_generated)
            # count_like = get_count_like(t_alias_generated)

            count_followed = 4471
            count_follower = 6211
            count_like = 8439

            # Costruisci l'oggetto UserProfileInfo
            user_profile_info = {
                "contentList": content_list,
                "bookedList": booked_list,
                "likedList": liked_list,
                "countFollowed": count_followed,
                "countFollower": count_follower,
                "countLike": count_like,
                "isPublic": True  # user_info.get("is_public", True)
            }

            # Costruisci il corpo della risposta come oggetto JSON
            response_body = json.dumps({"user_profile_info": user_profile_info})

            return HttpResponse(
                body=response_body,
                status_code=200,
                mimetype='application/json'
            )

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return HttpResponse(
                "Si è verificato un errore durante il recupero delle informazioni utente.",
                status_code=500
            )

    else:
        return HttpResponse(
            status_code=404
        )
