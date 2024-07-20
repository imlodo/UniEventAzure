import json
import logging
import os
import azure.functions as func
import jwt
from pymongo import MongoClient

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
users_collection = db.Users
discussion_collection = db.CONTENT_DISCUSSION
discussion_like_collection = db.DISCUSSION_LIKE


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
        t_username = decoded_token.get('username')
        if not t_username:
            return func.HttpResponse("Token non contiene un username valido.", status_code=401)

        content_id = req.params.get('content_id')
        if not content_id:
            return func.HttpResponse(
                "Il parametro content_id è obbligatorio.",
                status_code=400
            )

        # Recupera i commenti per il content_id dato
        # comments = discussion_collection.find({"content_id": content_id, "parent_discussion_id": {"$exists": False}})
        comment_list = [
            {
                "content_id": "123456",
                "discussion_id": "disc_001",
                "body": "Questo è il commento principale 1.",
                "like_count": 10,
                "t_user": {
                    "id": 1,
                    "t_name": "Mario Rossi",
                    "t_follower_number": 1000,
                    "t_alias_generated": "mariorossi",
                    "t_description": "Appassionato di tecnologia e innovazione.",
                    "t_profile_photo": "/assets/img/example_artist_image.jpg",
                    "t_type": 1,
                    "is_verified": True,
                    "type": "Utenti"
                },
                "created_date": "2024-07-01T12:34:56.789Z",
                "is_liked_by_current_user": True,
                "children": [],
                "t_alias_generated_reply": "mariobaldi"
            },
            {
                "content_id": "123456",
                "discussion_id": "disc_002",
                "body": "Questo è il commento principale 2.",
                "like_count": 5,
                "t_user": {
                    "id": 2,
                    "t_name": "Giulia Bianchi",
                    "t_follower_number": 500,
                    "t_alias_generated": "giuliabianchi",
                    "t_description": "Amo il design e l'arte.",
                    "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                    "t_type": 1,
                    "is_verified": False,
                    "type": "Utenti"
                },
                "created_date": "2024-07-02T14:56:23.123Z",
                "is_liked_by_current_user": False,
                "children": [
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_003",
                        "body": "Questo è un commento figlio del commento principale 2.",
                        "like_count": 3,
                        "t_user": {
                            "id": 3,
                            "t_name": "Luca Verdi",
                            "t_follower_number": 300,
                            "t_alias_generated": "lucaverdi",
                            "t_description": "Fotografo e viaggiatore.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": True,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-03T16:45:23.456Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "giuliabianchi"
                    }
                ]
            },
            {
                "content_id": "123456",
                "discussion_id": "disc_004",
                "body": "Questo è il commento principale 3.",
                "like_count": 8,
                "t_user": {
                    "id": 4,
                    "t_name": "Francesca Neri",
                    "t_follower_number": 800,
                    "t_alias_generated": "francescaneri",
                    "t_description": "Scrittrice e poetessa.",
                    "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                    "t_type": 1,
                    "is_verified": True,
                    "type": "Utenti"
                },
                "created_date": "2024-07-04T10:20:30.123Z",
                "is_liked_by_current_user": True,
                "children": [
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_005",
                        "body": "Questo è un commento figlio 1 del commento principale 3.",
                        "like_count": 4,
                        "t_user": {
                            "id": 5,
                            "t_name": "Alessandro Bianchi",
                            "t_follower_number": 600,
                            "t_alias_generated": "alessandrobianchi",
                            "t_description": "Musicista e compositore.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": False,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-04T11:45:50.456Z",
                        "is_liked_by_current_user": True,
                        "t_alias_generated_reply": "francescaneri"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_006",
                        "body": "Questo è un commento figlio 2 del commento principale 3.",
                        "like_count": 2,
                        "t_user": {
                            "id": 6,
                            "t_name": "Lucia Neri",
                            "t_follower_number": 700,
                            "t_alias_generated": "lucianeri",
                            "t_description": "Attrice e regista.",
                            "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                            "t_type": 1,
                            "is_verified": False,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-04T12:30:45.789Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "francescaneri"
                    }
                ]
            },
            {
                "content_id": "123456",
                "discussion_id": "disc_007",
                "body": "Questo è il commento principale 4.",
                "like_count": 12,
                "t_user": {
                    "id": 7,
                    "t_name": "Gianni Esposito",
                    "t_follower_number": 1500,
                    "t_alias_generated": "gianniesposito",
                    "t_description": "Fotografo professionista.",
                    "t_profile_photo": "/assets/img/example_artist_image.jpg",
                    "t_type": 1,
                    "is_verified": True,
                    "type": "Utenti"
                },
                "created_date": "2024-07-05T09:20:15.456Z",
                "is_liked_by_current_user": False,
                "children": [
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_008",
                        "body": "Questo è un commento figlio 1 del commento principale 4.",
                        "like_count": 6,
                        "t_user": {
                            "id": 8,
                            "t_name": "Sara De Luca",
                            "t_follower_number": 1200,
                            "t_alias_generated": "saradeluca",
                            "t_description": "Artista e pittrice.",
                            "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                            "t_type": 1,
                            "is_verified": False,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-05T10:50:20.789Z",
                        "is_liked_by_current_user": True,
                        "t_alias_generated_reply": "gianniesposito"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_009",
                        "body": "Questo è un commento figlio 2 del commento principale 4.",
                        "like_count": 3,
                        "t_user": {
                            "id": 9,
                            "t_name": "Carlo Bruni",
                            "t_follower_number": 1100,
                            "t_alias_generated": "carlobruni",
                            "t_description": "Regista e sceneggiatore.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": True,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-05T11:40:35.456Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "gianniesposito"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_010",
                        "body": "Questo è un commento figlio 3 del commento principale 4.",
                        "like_count": 1,
                        "t_user": {
                            "id": 10,
                            "t_name": "Elena Moretti",
                            "t_follower_number": 1300,
                            "t_alias_generated": "elenamoretti",
                            "t_description": "Giornalista e scrittrice.",
                            "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                            "t_type": 1,
                            "is_verified": False,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-05T12:25:40.789Z",
                        "is_liked_by_current_user": True,
                        "t_alias_generated_reply": "gianniesposito"
                    }
                ]
            },
            {
                "content_id": "123456",
                "discussion_id": "disc_011",
                "body": "Questo è il commento principale 5.",
                "like_count": 9,
                "t_user": {
                    "id": 11,
                    "t_name": "Paola Rossi",
                    "t_follower_number": 900,
                    "t_alias_generated": "paolarossi",
                    "t_description": "Cantante e musicista.",
                    "t_profile_photo": "/assets/img/example_artist_image.jpg",
                    "t_type": 1,
                    "is_verified": True,
                    "type": "Utenti"
                },
                "created_date": "2024-07-06T08:15:20.456Z",
                "is_liked_by_current_user": False,
                "children": [
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_012",
                        "body": "Questo è un commento figlio 1 del commento principale 5.",
                        "like_count": 7,
                        "t_user": {
                            "id": 12,
                            "t_name": "Marco Bianchi",
                            "t_follower_number": 750,
                            "t_alias_generated": "marcobianchi",
                            "t_description": "Attore e produttore.",
                            "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                            "t_type": 1,
                            "is_verified": False,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-06T09:50:10.789Z",
                        "is_liked_by_current_user": True,
                        "t_alias_generated_reply": "paolarossi"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_013",
                        "body": "Questo è un commento figlio 2 del commento principale 5.",
                        "like_count": 5,
                        "t_user": {
                            "id": 13,
                            "t_name": "Anna Verdi",
                            "t_follower_number": 850,
                            "t_alias_generated": "annaverdi",
                            "t_description": "Artista e fotografa.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": True,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-06T10:30:25.456Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "paolarossi"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_014",
                        "body": "Questo è un commento figlio 3 del commento principale 5.",
                        "like_count": 2,
                        "t_user": {
                            "id": 14,
                            "t_name": "Davide Esposito",
                            "t_follower_number": 950,
                            "t_alias_generated": "davideesposito",
                            "t_description": "Poeta e scrittore.",
                            "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                            "t_type": 1,
                            "is_verified": False,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-06T11:45:40.789Z",
                        "is_liked_by_current_user": True,
                        "t_alias_generated_reply": "paolarossi"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_015",
                        "body": "Questo è un commento figlio 4 del commento principale 5.",
                        "like_count": 1,
                        "t_user": {
                            "id": 15,
                            "t_name": "Luca Bianchi",
                            "t_follower_number": 1050,
                            "t_alias_generated": "lucabianchi",
                            "t_description": "Regista e produttore.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": True,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-06T12:55:50.456Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "paolarossi"
                    }
                ]
            },
            {
                "content_id": "123456",
                "discussion_id": "disc_016",
                "body": "Questo è il commento principale 6.",
                "like_count": 11,
                "t_user": {
                    "id": 16,
                    "t_name": "Elisa Neri",
                    "t_follower_number": 1400,
                    "t_alias_generated": "elisaneri",
                    "t_description": "Blogger e influencer.",
                    "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                    "t_type": 1,
                    "is_verified": False,
                    "type": "Utenti"
                },
                "created_date": "2024-07-07T07:45:20.789Z",
                "is_liked_by_current_user": True,
                "children": [
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_017",
                        "body": "Questo è un commento figlio 1 del commento principale 6.",
                        "like_count": 9,
                        "t_user": {
                            "id": 17,
                            "t_name": "Michele Esposito",
                            "t_follower_number": 1350,
                            "t_alias_generated": "micheleesposito",
                            "t_description": "Designer e architetto.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": True,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-07T08:20:30.123Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "elisaneri"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_018",
                        "body": "Questo è un commento figlio 2 del commento principale 6.",
                        "like_count": 6,
                        "t_user": {
                            "id": 18,
                            "t_name": "Silvia Rossi",
                            "t_follower_number": 1250,
                            "t_alias_generated": "silviarossi",
                            "t_description": "Fotografa e artista.",
                            "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                            "t_type": 1,
                            "is_verified": False,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-07T09:10:40.456Z",
                        "is_liked_by_current_user": True,
                        "t_alias_generated_reply": "elisaneri"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_019",
                        "body": "Questo è un commento figlio 3 del commento principale 6.",
                        "like_count": 3,
                        "t_user": {
                            "id": 19,
                            "t_name": "Giorgio Bianchi",
                            "t_follower_number": 1150,
                            "t_alias_generated": "giorgiobianchi",
                            "t_description": "Scrittore e poeta.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": True,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-07T10:05:50.789Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "elisaneri"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_020",
                        "body": "Questo è un commento figlio 4 del commento principale 6.",
                        "like_count": 1,
                        "t_user": {
                            "id": 20,
                            "t_name": "Laura Verdi",
                            "t_follower_number": 1450,
                            "t_alias_generated": "lauraverdi",
                            "t_description": "Attrice e sceneggiatrice.",
                            "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                            "t_type": 1,
                            "is_verified": False,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-07T11:00:30.123Z",
                        "is_liked_by_current_user": True,
                        "t_alias_generated_reply": "elisaneri"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_021",
                        "body": "Questo è un commento figlio 5 del commento principale 6.",
                        "like_count": 2,
                        "t_user": {
                            "id": 21,
                            "t_name": "Fabio Esposito",
                            "t_follower_number": 1550,
                            "t_alias_generated": "fabioesposito",
                            "t_description": "Musicista e compositore.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": True,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-07T11:45:20.456Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "elisaneri"
                    }
                ]
            },
            {
                "content_id": "123456",
                "discussion_id": "disc_022",
                "body": "Questo è il commento principale 7.",
                "like_count": 6,
                "t_user": {
                    "id": 22,
                    "t_name": "Martina Rossi",
                    "t_follower_number": 1000,
                    "t_alias_generated": "martinarossi",
                    "t_description": "Artista e designer.",
                    "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                    "t_type": 1,
                    "is_verified": False,
                    "type": "Utenti"
                },
                "created_date": "2024-07-08T08:30:15.456Z",
                "is_liked_by_current_user": True,
                "children": [
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_023",
                        "body": "Questo è un commento figlio 1 del commento principale 7.",
                        "like_count": 4,
                        "t_user": {
                            "id": 23,
                            "t_name": "Roberto Bianchi",
                            "t_follower_number": 850,
                            "t_alias_generated": "robertobianchi",
                            "t_description": "Regista e sceneggiatore.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": True,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-08T09:50:30.789Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "martinarossi"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_024",
                        "body": "Questo è un commento figlio 2 del commento principale 7.",
                        "like_count": 3,
                        "t_user": {
                            "id": 24,
                            "t_name": "Chiara Neri",
                            "t_follower_number": 900,
                            "t_alias_generated": "chiaraneri",
                            "t_description": "Fotografa e pittrice.",
                            "t_profile_photo": "/assets/img/userExampleImg.jpeg",
                            "t_type": 1,
                            "is_verified": False,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-08T10:20:40.123Z",
                        "is_liked_by_current_user": True,
                        "t_alias_generated_reply": "martinarossi"
                    },
                    {
                        "content_id": "123456",
                        "discussion_id": "disc_025",
                        "body": "Questo è un commento figlio 3 del commento principale 7.",
                        "like_count": 2,
                        "t_user": {
                            "id": 25,
                            "t_name": "Andrea Verdi",
                            "t_follower_number": 950,
                            "t_alias_generated": "andreaverdi",
                            "t_description": "Attore e produttore.",
                            "t_profile_photo": "/assets/img/example_artist_image.jpg",
                            "t_type": 1,
                            "is_verified": True,
                            "type": "Utenti"
                        },
                        "created_date": "2024-07-08T11:00:50.456Z",
                        "is_liked_by_current_user": False,
                        "t_alias_generated_reply": "martinarossi"
                    }
                ]
            }
        ]

        # for comment in comments:
        #     discussion_id = comment.get('discussion_id')
        #     is_liked_by_current_user = discussion_like_collection.count_documents({
        #         "discussion_id": discussion_id,
        #         "t_username": t_username
        #     }) > 0
        # 
        #     # Recupera l'utente che ha scritto il commento
        #     user = users_collection.find_one({"t_alias_generated": comment.get('t_alias_generated')})
        #     t_user = {
        #         "id": user.get('_id'),
        #         "t_name": user.get('t_name'),
        #         "t_follower_number": user.get('t_follower_number'),
        #         "t_alias_generated": user.get('t_alias_generated'),
        #         "t_description": user.get('t_description'),
        #         "t_profile_photo": user.get('t_profile_photo'),
        #         "t_type": user.get('t_type'),
        #         "is_verified": user.get('is_verified'),
        #         "type": "Utenti"
        #     }
        # 
        #     # Recupera i commenti figli
        #     children = []
        #     child_comments = discussion_collection.find({"parent_discussion_id": discussion_id})
        #     for child in child_comments:
        #         child_is_liked = discussion_like_collection.count_documents({
        #             "discussion_id": child.get('discussion_id'),
        #             "t_username": t_username
        #         }) > 0
        # 
        #         child_user = users_collection.find_one({"t_alias_generated": child.get('t_alias_generated')})
        #         child_t_user = {
        #             "id": child_user.get('_id'),
        #             "t_name": child_user.get('t_name'),
        #             "t_follower_number": child_user.get('t_follower_number'),
        #             "t_alias_generated": child_user.get('t_alias_generated'),
        #             "t_description": child_user.get('t_description'),
        #             "t_profile_photo": child_user.get('t_profile_photo'),
        #             "t_type": child_user.get('t_type'),
        #             "is_verified": child_user.get('is_verified'),
        #             "type": "Utenti"
        #         }
        # 
        #         children.append({
        #             "content_id": child.get('content_id'),
        #             "discussion_id": child.get('discussion_id'),
        #             "body": child.get('body'),
        #             "like_count": discussion_like_collection.count_documents({"discussion_id": child.get('discussion_id')}),
        #             "t_user": child_t_user,
        #             "created_date": child.get('created_date'),
        #             "is_liked_by_current_user": child_is_liked,
        #             "t_alias_generated_reply": child.get('reply_alias_generated')
        #         })
        # 
        #     comment_list.append({
        #         "content_id": comment.get('content_id'),
        #         "discussion_id": comment.get('discussion_id'),
        #         "body": comment.get('body'),
        #         "like_count": discussion_like_collection.count_documents({"discussion_id": discussion_id}),
        #         "t_user": t_user,
        #         "created_date": comment.get('created_date'),
        #         "is_liked_by_current_user": is_liked_by_current_user,
        #         "children": children
        #     })

        return func.HttpResponse(
            json.dumps(comment_list, default=str),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Errore: {e}")
        return func.HttpResponse(
            "Errore durante l'elaborazione della richiesta.",
            status_code=500
        )
