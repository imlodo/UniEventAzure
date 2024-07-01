import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import azure.functions as func
import jwt

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Ottieni la stringa di connessione dal file delle variabili d'ambiente
connectString = os.getenv("DB_CONNECTION_STRING")

client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona la collezione per i messaggi e gli utenti
messages_collection = db.Messages
users_collection = db.Users

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Ottieni il token JWT dall'header Authorization
        auth_header = req.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return func.HttpResponse("Autorizzazione non valida.", status_code=401)

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

        # Recupera i messaggi dal database
        # messages = messages_collection.find(
        #     {"$or": [{"user_at": username}, {"user_from": username}]}
        # )
        # 
        # # Creazione di un dizionario per tracciare gli utenti unici e l'ultimo messaggio
        # unique_users = {}
        # for message in messages:
        #     # Recupera i dettagli dell'utente dal database degli utenti
        #     user_at = users_collection.find_one({"username": message["user_at"]})
        #     user_from = users_collection.find_one({"username": message["user_from"]})
        # 
        #     if not user_at or not user_from:
        #         continue
        # 
        #     user_key = user_at["alias_generated"] if user_at["username"] != username else user_from["alias_generated"]
        #     if user_key not in unique_users:
        #         unique_users[user_key] = {
        #             "userChat": {
        #                 "t_name": user_at["name"] if user_at["username"] != username else user_from["name"],
        #                 "t_surname": user_at["surname"] if user_at["username"] != username else user_from["surname"],
        #                 "t_alias_generated": user_key,
        #                 "t_profile_photo": user_at.get("profile_photo") if user_at["username"] != username else user_from.get("profile_photo"),
        #                 "t_type": user_at["type"] if user_at["username"] != username else user_from["type"]
        #             },
        #             "messages": [{
        #                 "user_at": user_at,
        #                 "user_from": user_from,
        #                 "message": message["message"],
        #                 "dateTime": message["dateTime"]
        #             }]
        #         }
        #     else:
        #         # Aggiorna con l'ultimo messaggio se è più recente
        #         if message["dateTime"] > unique_users[user_key]["messages"][0]["dateTime"]:
        #             unique_users[user_key]["messages"][0] = {
        #                 "user_at": user_at,
        #                 "user_from": user_from,
        #                 "message": message["message"],
        #                 "dateTime": message["dateTime"]
        #             }
        # 
        # # Creazione della lista di utenti per la risposta
        # user_list = list(unique_users.values())

        user_list = [
            {
                "userChat": {
                    "t_name": "Marco",
                    "t_surname": "Rossi",
                    "t_alias_generated": "marcorossi",
                    "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                    "t_type": "ARTIST"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Marco",
                            "t_surname": "Rossi",
                            "t_alias_generated": "marcorossi",
                            "t_profile_photo": "https://staff.polito.it/mario.baldi/images/Mario%20202004.jpg",
                            "t_type": "ARTIST"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Ciao Marco!",
                        "dateTime": "2024-06-20T10:30:00Z"
                    }
                ]
            },
            {
                "userChat": {
                    "t_name": "Luca",
                    "t_surname": "Bianchi",
                    "t_alias_generated": "JD",
                    "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                    "t_type": "CREATOR"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Wewe, mi sto scrivendo da solo",
                        "dateTime": "2024-06-20T11:00:00Z"
                    }
                ]
            },
            {
                "userChat": {
                    "t_name": "Giulia",
                    "t_surname": "Verdi",
                    "t_alias_generated": "giuliaverdi",
                    "t_profile_photo": "https://media.licdn.com/dms/image/D4D22AQFqRuP8yStw4w/feedshare-shrink_2048_1536/0/1695978679787?e=2147483647&v=beta&t=B7j5DnOemKkcsgORmlNnx6wJhWcLpA26Q0_aX5Ce4Bw",
                    "t_type": "COMPANY"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Giulia",
                            "t_surname": "Verdi",
                            "t_alias_generated": "giuliaverdi",
                            "t_profile_photo": "https://media.licdn.com/dms/image/D4D22AQFqRuP8yStw4w/feedshare-shrink_2048_1536/0/1695978679787?e=2147483647&v=beta&t=B7j5DnOemKkcsgORmlNnx6wJhWcLpA26Q0_aX5Ce4Bw",
                            "t_type": "COMPANY"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Ciao Giulia!",
                        "dateTime": "2024-06-20T11:30:00Z"
                    }
                ]
            },
            {
                "userChat": {
                    "t_name": "Anna",
                    "t_surname": "Neri",
                    "t_alias_generated": "annaneri",
                    "t_profile_photo": "https://media.licdn.com/dms/image/D4E03AQEIyrpRj7DcWg/profile-displayphoto-shrink_200_200/0/1692461678582?e=2147483647&v=beta&t=WVxFj4sdlwOpmf-bI-QXO9WAGQXAehJmitP8hrvqhik",
                    "t_type": "ARTIST"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Anna",
                            "t_surname": "Neri",
                            "t_alias_generated": "annaneri",
                            "t_profile_photo": "https://media.licdn.com/dms/image/D4E03AQEIyrpRj7DcWg/profile-displayphoto-shrink_200_200/0/1692461678582?e=2147483647&v=beta&t=WVxFj4sdlwOpmf-bI-QXO9WAGQXAehJmitP8hrvqhik",
                            "t_type": "ARTIST"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Ciao Anna!",
                        "dateTime": "2024-06-20T12:00:00Z"
                    }
                ]
            },
            {
                "userChat": {
                    "t_name": "Francesco",
                    "t_surname": "Russo",
                    "t_alias_generated": "francescorusso",
                    "t_profile_photo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTD6X2telTCT0e3EbzTOH9aPCr0-Ab7U-Dasg&s",
                    "t_type": "CREATOR"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Francesco",
                            "t_surname": "Russo",
                            "t_alias_generated": "francescorusso",
                            "t_profile_photo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTD6X2telTCT0e3EbzTOH9aPCr0-Ab7U-Dasg&s",
                            "t_type": "CREATOR"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Ciao Francesco!",
                        "dateTime": "2024-06-20T12:30:00Z"
                    }
                ]
            },
            {
                "userChat": {
                    "t_name": "Chiara",
                    "t_surname": "Ferrari",
                    "t_alias_generated": "chiaraferrari",
                    "t_profile_photo": "https://quifinanza.it/wp-content/uploads/sites/5/2024/01/Chiara-Ferragni.jpg?w=388&h=219&quality=80&strip=all&crop=1",
                    "t_type": "COMPANY"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Chiara",
                            "t_surname": "Ferrari",
                            "t_alias_generated": "chiaraferrari",
                            "t_profile_photo": "https://quifinanza.it/wp-content/uploads/sites/5/2024/01/Chiara-Ferragni.jpg?w=388&h=219&quality=80&strip=all&crop=1",
                            "t_type": "COMPANY"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Ciao Chiara!",
                        "dateTime": "2024-06-20T13:00:00Z"
                    }
                ]
            },
            {
                "userChat": {
                    "t_name": "Matteo",
                    "t_surname": "Gallo",
                    "t_alias_generated": "matteogallo",
                    "t_profile_photo": "https://www.gedistatic.it/content/gnn/img/lasentinella/2023/08/17/190653391-b91ecff5-169e-408b-849e-7954baf120ee.jpg",
                    "t_type": "ARTIST"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Matteo",
                            "t_surname": "Gallo",
                            "t_alias_generated": "matteogallo",
                            "t_profile_photo": "https://www.gedistatic.it/content/gnn/img/lasentinella/2023/08/17/190653391-b91ecff5-169e-408b-849e-7954baf120ee.jpg",
                            "t_type": "ARTIST"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Ciao Matteo!",
                        "dateTime": "2024-06-20T13:30:00Z"
                    }
                ]
            },
            {
                "userChat": {
                    "t_name": "Elena",
                    "t_surname": "Greco",
                    "t_alias_generated": "elenagreco",
                    "t_profile_photo": "https://www.hallofseries.com/wp-content/uploads/2020/05/elena-greco.jpg",
                    "t_type": "CREATOR"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Elena",
                            "t_surname": "Greco",
                            "t_alias_generated": "elenagreco",
                            "t_profile_photo": "https://www.hallofseries.com/wp-content/uploads/2020/05/elena-greco.jpg",
                            "t_type": "CREATOR"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Ciao Elena!",
                        "dateTime": "2024-06-20T14:00:00Z"
                    }
                ]
            },
            {
                "userChat": {
                    "t_name": "Paolo",
                    "t_surname": "Conti",
                    "t_alias_generated": "paoloconti",
                    "t_profile_photo": "https://upload.wikimedia.org/wikipedia/it/e/ee/Paolo_Conti_-_AS_Roma_1973-74.jpg",
                    "t_type": "COMPANY"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Paolo",
                            "t_surname": "Conti",
                            "t_alias_generated": "paoloconti",
                            "t_profile_photo": "https://upload.wikimedia.org/wikipedia/it/e/ee/Paolo_Conti_-_AS_Roma_1973-74.jpg",
                            "t_type": "COMPANY"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Ciao Paolo!",
                        "dateTime": "2024-06-20T14:30:00Z"
                    }
                ]
            },
            {
                "userChat": {
                    "t_name": "Martina",
                    "t_surname": "Santoro",
                    "t_alias_generated": "martinasantoro",
                    "t_profile_photo": "https://pbs.twimg.com/media/EHpWsxKXYAAKBmw.jpg:large",
                    "t_type": "ARTIST"
                },
                "messages": [
                    {
                        "user_at": {
                            "t_name": "Martina",
                            "t_surname": "Santoro",
                            "t_alias_generated": "martinasantoro",
                            "t_profile_photo": "https://pbs.twimg.com/media/EHpWsxKXYAAKBmw.jpg:large",
                            "t_type": "ARTIST"
                        },
                        "user_from": {
                            "t_name": "Luca",
                            "t_surname": "Bianchi",
                            "t_alias_generated": "JD",
                            "t_profile_photo": "https://cdn.21buttons.com/posts/640x799/a4f98433206c47f3ac3b47039996f26f_1080x1349.jpg",
                            "t_type": "CREATOR"
                        },
                        "message": "Ciao Martina!",
                        "dateTime": "2024-06-20T15:00:00Z"
                    }
                ]
            }
        ]
        # Ordinamento della lista in base agli ultimi utenti scritti
        user_list = sorted(user_list, key=lambda x: x["messages"][0]["dateTime"], reverse=True)

        response_body = json.dumps(user_list, default=str)
        return func.HttpResponse(response_body, mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return func.HttpResponse("Si è verificato un errore durante il recupero delle chat.", status_code=500)
