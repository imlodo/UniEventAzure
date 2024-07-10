import logging
import os
import json

import jwt
from bson import ObjectId
from pymongo import MongoClient
import azure.functions as func

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
users_collection = db.User
follow_user_collection = db.FollowUser


def get_followed_users(t_username, limit=None):
    followed_aliases = follow_user_collection.find({"t_alias_generated_from": t_username},
                                                   {"t_alias_generated_to": 1, "_id": 0})
    followed_aliases = [follow['t_alias_generated_to'] for follow in followed_aliases]

    query = {"t_alias_generated": {"$in": followed_aliases}}
    users = users_collection.find(query)

    user_list = []
    for user in users:
        user_dict = {
            "_id": str(user["_id"]),
            "t_username": user.get("t_username", ""),
            "t_password": user.get("t_password", ""),
            "t_name": user.get("t_name", ""),
            "t_surname": user.get("t_surname", ""),
            "t_alias_generated": user.get("t_alias_generated", ""),
            "t_description": user.get("t_description", ""),
            "t_profile_photo": user.get("t_profile_photo", ""),
            "is_verified": user.get("is_verified", False),
            "t_type": user.get("t_type", ""),
            "t_role": "Utente"
        }
        user_list.append(user_dict)

    if limit:
        user_list = user_list[:limit]

    return user_list


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    if req.method == 'GET':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            alias_generated = req.params.get("t_alias_generated")
            if alias_generated:
                print(alias_generated)
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

            limit = req.params.get('limit')
            if limit:
                limit = int(limit)

            # followed_users = get_followed_users(t_username, limit)

            followed_users = [
                {
                    "_id": "60b8d295f8ba2b1b78b5a4d1",
                    "t_username": "followed_user1",
                    "t_password": "hashed_password",
                    "t_name": "John",
                    "t_surname": "Doe",
                    "t_alias_generated": "johndoe",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "USER_TYPE",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4d2",
                    "t_username": "followed_user2",
                    "t_password": "hashed_password",
                    "t_name": "Jane",
                    "t_surname": "Doe",
                    "t_alias_generated": "janedoe",
                    "t_description": "Lorem ipsum dolor sit amet.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "USER_TYPE",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4d3",
                    "t_username": "followed_user3",
                    "t_password": "hashed_password",
                    "t_name": "Alice",
                    "t_surname": "Smith",
                    "t_alias_generated": "alicesmith",
                    "t_description": "Passionate about technology.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "CREATOR",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4d4",
                    "t_username": "followed_user4",
                    "t_password": "hashed_password",
                    "t_name": "Bob",
                    "t_surname": "Brown",
                    "t_alias_generated": "bobbrown",
                    "t_description": "Loves to travel and explore.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4d5",
                    "t_username": "followed_user5",
                    "t_password": "hashed_password",
                    "t_name": "Charlie",
                    "t_surname": "Davis",
                    "t_alias_generated": "charliedavis",
                    "t_description": "Food blogger and chef.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4d6",
                    "t_username": "followed_user6",
                    "t_password": "hashed_password",
                    "t_name": "Diana",
                    "t_surname": "Evans",
                    "t_alias_generated": "dianaevans",
                    "t_description": "Fitness enthusiast.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4d7",
                    "t_username": "followed_user7",
                    "t_password": "hashed_password",
                    "t_name": "Edward",
                    "t_surname": "Garcia",
                    "t_alias_generated": "edwardgarcia",
                    "t_description": "Photographer and visual storyteller.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4d8",
                    "t_username": "followed_user8",
                    "t_password": "hashed_password",
                    "t_name": "Fiona",
                    "t_surname": "Harris",
                    "t_alias_generated": "fionaharris",
                    "t_description": "Writer and blogger.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4d9",
                    "t_username": "followed_user9",
                    "t_password": "hashed_password",
                    "t_name": "George",
                    "t_surname": "Clark",
                    "t_alias_generated": "georgeclark",
                    "t_description": "Musician and composer.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4da",
                    "t_username": "followed_user10",
                    "t_password": "hashed_password",
                    "t_name": "Hannah",
                    "t_surname": "Jackson",
                    "t_alias_generated": "hannahjackson",
                    "t_description": "Digital marketer.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4db",
                    "t_username": "followed_user11",
                    "t_password": "hashed_password",
                    "t_name": "Ian",
                    "t_surname": "Kelly",
                    "t_alias_generated": "iankelly",
                    "t_description": "Tech entrepreneur.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4dc",
                    "t_username": "followed_user12",
                    "t_password": "hashed_password",
                    "t_name": "Jane",
                    "t_surname": "Lee",
                    "t_alias_generated": "janelee",
                    "t_description": "Fashion designer.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4dd",
                    "t_username": "followed_user13",
                    "t_password": "hashed_password",
                    "t_name": "Kyle",
                    "t_surname": "Martin",
                    "t_alias_generated": "kylemartin",
                    "t_description": "Sports enthusiast.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4de",
                    "t_username": "followed_user14",
                    "t_password": "hashed_password",
                    "t_name": "Laura",
                    "t_surname": "Nelson",
                    "t_alias_generated": "lauranelson",
                    "t_description": "Graphic designer.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4df",
                    "t_username": "followed_user15",
                    "t_password": "hashed_password",
                    "t_name": "Mark",
                    "t_surname": "Owens",
                    "t_alias_generated": "markowens",
                    "t_description": "Travel blogger.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4e0",
                    "t_username": "followed_user16",
                    "t_password": "hashed_password",
                    "t_name": "Nancy",
                    "t_surname": "Parker",
                    "t_alias_generated": "nancyparker",
                    "t_description": "Animal lover and activist.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4e1",
                    "t_username": "followed_user17",
                    "t_password": "hashed_password",
                    "t_name": "Oliver",
                    "t_surname": "Quinn",
                    "t_alias_generated": "oliverquinn",
                    "t_description": "Software developer.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4e2",
                    "t_username": "followed_user18",
                    "t_password": "hashed_password",
                    "t_name": "Paula",
                    "t_surname": "Robinson",
                    "t_alias_generated": "paularobinson",
                    "t_description": "Nutritionist and wellness coach.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": False,
                    "t_type": "CREATOR",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4e3",
                    "t_username": "followed_user19",
                    "t_password": "hashed_password",
                    "t_name": "Quinn",
                    "t_surname": "Stewart",
                    "t_alias_generated": "quinnstewart",
                    "t_description": "Movie critic and reviewer.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                },
                {
                    "_id": "60b8d295f8ba2b1b78b5a4e4",
                    "t_username": "followed_user20",
                    "t_password": "hashed_password",
                    "t_name": "Rachel",
                    "t_surname": "Taylor",
                    "t_alias_generated": "racheltaylor",
                    "t_description": "Environmental scientist.",
                    "t_profile_photo": "http://localhost:4200/assets/img/userExampleImg.jpeg",
                    "is_verified": True,
                    "t_type": "ARTIST",
                    "t_role": "Utente"
                }
            ]

            if limit:
                followed_users = followed_users[:limit]

            return func.HttpResponse(
                json.dumps({"followed_users": followed_users}, default=str),
                status_code=200,
                mimetype='application/json'
            )
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante il recupero degli utenti seguiti.",
                status_code=500
            )
    else:
        return func.HttpResponse(
            status_code=404
        )
