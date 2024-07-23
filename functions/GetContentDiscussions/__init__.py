import json
import logging
import os
import azure.functions as func
import jwt
from bson import ObjectId
from pymongo import MongoClient

# Connessione al cluster di Azure Cosmos DB for MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database
db = client.unieventmongodb

# Seleziona le collezioni
users_collection = db.Users
discussion_collection = db.ContentDiscussion
discussion_like_collection = db.DiscussionLike


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
        comments = discussion_collection.find({"content_id": ObjectId(content_id)})
        comment_list = []
        for comment in comments:
            discussion_id = comment.get('_id')
            is_liked_by_current_user = discussion_like_collection.count_documents({
                "discussion_id": ObjectId(discussion_id),
                "t_username": t_username
            }) > 0

            # Recupera l'utente che ha scritto il commento
            user = users_collection.find_one({"t_alias_generated": comment.get('t_alias_generated')})

            # Recupera i commenti figli
            children = []
            child_comments = discussion_collection.find({"parent_discussion_id": ObjectId(discussion_id)})
            for child in child_comments:
                child_is_liked = discussion_like_collection.count_documents({
                    "discussion_id": ObjectId(child.get('discussion_id')),
                    "t_username": user.get("t_username")
                }) > 0

                child_user = users_collection.find_one({"t_alias_generated": child.get('t_alias_generated')})
                child_t_user = {
                    "id": child_user.get('_id'),
                    "t_name": child_user.get('t_name'),
                    "t_follower_number": child_user.get('t_follower_number'),
                    "t_alias_generated": child_user.get('t_alias_generated'),
                    "t_description": child_user.get('t_description'),
                    "t_profile_photo": child_user.get('t_profile_photo'),
                    "t_type": child_user.get('t_type'),
                    "is_verified": child_user.get('is_verified'),
                    "type": "Utenti"
                }

                children.append({
                    "content_id": child.get('content_id'),
                    "discussion_id": child.get('discussion_id'),
                    "body": child.get('body'),
                    "like_count": discussion_like_collection.count_documents(
                        {"discussion_id": ObjectId(child.get('discussion_id'))}),
                    "t_user": child_t_user,
                    "created_date": child.get('created_date'),
                    "is_liked_by_current_user": child_is_liked,
                    "t_alias_generated_reply": child.get('reply_alias_generated')
                })

            comment_list.append({
                "content_id": str(comment.get('content_id')),
                "discussion_id": str(comment.get('_id')),
                "body": comment.get('body'),
                "like_count": discussion_like_collection.count_documents({"discussion_id": ObjectId(discussion_id)}),
                "t_user": user,
                "created_date": comment.get('created_date'),
                "is_liked_by_current_user": is_liked_by_current_user,
                "children": children
            })

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
