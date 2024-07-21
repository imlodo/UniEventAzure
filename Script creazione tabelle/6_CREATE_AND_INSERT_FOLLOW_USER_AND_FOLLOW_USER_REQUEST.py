import os
import pymongo
import random
from pymongo import MongoClient
from datetime import datetime

# Connessione al database MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
user_settings_collection = db.UserSettings
follow_user_collection = db.FollowUser
follow_user_request_collection = db.FollowUserRequest
users_collection = db.Users

def insert_follow_records():
    # Recupera tutti gli utenti con `privacy.visibility.private_account` = True o False
    users_with_settings = user_settings_collection.find()

    for user_settings in users_with_settings:
        t_username = user_settings.get("t_username")
        private_account = user_settings.get("privacy", {}).get("visibility", {}).get("private_account", False)
        
        if not t_username:
            continue

        # Trova i dettagli dell'utente
        user = users_collection.find_one({"t_username": t_username})
        if not user:
            continue

        t_alias_generated = user.get("t_alias_generated")
        t_role = user.get("t_role")

        # Condizione per `FollowUserRequest`
        if private_account and t_role == "Utente":
            # Trova un altro utente con ruolo "Utente"
            other_users = users_collection.find({
                "t_alias_generated": {"$ne": t_alias_generated},
                "t_role": "Utente"
            })
            
            other_users_list = list(other_users)
            if other_users_list:
                t_alias_generated_from = t_alias_generated
                t_alias_generated_to = random.choice(other_users_list).get("t_alias_generated")
                
                follow_user_request_record = {
                    "t_alias_generated_from": t_alias_generated_from,
                    "t_alias_generated_to": t_alias_generated_to,
                    "follow_date": datetime.utcnow()
                }
                follow_user_request_collection.insert_one(follow_user_request_record)
                print(f"FollowUserRequest inserito: {follow_user_request_record}")

        # Condizione per `FollowUser`
        elif not private_account and t_role == "Utente":
            # Trova un altro utente con ruolo "Utente"
            other_users = users_collection.find({
                "t_alias_generated": {"$ne": t_alias_generated},
                "t_role": "Utente"
            })
            
            other_users_list = list(other_users)
            if other_users_list:
                t_alias_generated_from = t_alias_generated
                t_alias_generated_to = random.choice(other_users_list).get("t_alias_generated")
                
                follow_user_record = {
                    "t_alias_generated_from": t_alias_generated_from,
                    "t_alias_generated_to": t_alias_generated_to,
                    "follow_date": datetime.utcnow()
                }
                follow_user_collection.insert_one(follow_user_record)
                print(f"FollowUser inserito: {follow_user_record}")

insert_follow_records()
