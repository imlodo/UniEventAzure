import os
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import string

# Connessione al cluster di MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
contents_collection = db.Contents
content_tags_collection = db.ContentTags
content_mentions_collection = db.ContentMentions
content_booked_collection = db.ContentBooked
content_discussion_collection = db.ContentDiscussion
discussion_likes_collection = db.DiscussionLike
content_likes_collection = db.ContentLike
event_location_collection = db.EventLocation
event_maps_collection = db.EventMaps
object_maps_collection = db.ObjectMaps
object_seats_collection = db.ObjectSeats
event_coupons_collection = db.EventCoupon
users_collection = db.User

# Dati di esempio per i topics e gli eventi
topics_aliases = ["davidestrianese", "mariobaldi", "francescoferrara"]
events_aliases = ["chiaraferragni", "salmo", "discosalerno", "discominori"]
all_aliases = topics_aliases + events_aliases
tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]  # Esempio di tag
cities = ["Rome", "Milan", "Naples", "Turin", "Palermo"]  # Esempio di città
provinces = ["RM", "MI", "NA", "TO", "PA"]  # Esempio di province
states = ["Italy"]  # Esempio di stati
locations = ["Stadium", "Concert Hall", "Theater", "Club", "Arena"]  # Esempio di location

# Funzione per generare una stringa casuale
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Recupera tutti gli utenti dal database
users = list(users_collection.find({}))

# Inserisci contenuti
def insert_contents():
    contents = []
    content_tags = []
    content_mentions = []
    content_booked = []
    content_discussions = []
    discussion_likes = []
    content_likes = []
    event_locations = []
    event_maps = []
    object_maps = []
    object_seats = []
    event_coupons = []
    
    # Genera un gruppo ID unico per gli eventi
    group_id = 1
    
    for i in range(30):
        content_type = "Topics" if i < 15 else "Eventi"  # 15 Topics e 15 Eventi
        t_alias_generated = random.choice(topics_aliases) if content_type == "Topics" else random.choice(events_aliases)
        
        content = {
            "n_group_id": group_id if content_type == "Eventi" else None,
            "t_alias_generated": t_alias_generated,
            "t_caption": f"Caption {random_string(8)}",
            "t_type": content_type,
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "t_image_link": f"https://example.com/image_{random_string(5)}.jpg",
            "t_video_link": f"https://example.com/video_{random_string(5)}.mp4" if random.random() > 0.5 else "",
            "t_privacy": random.choice(["public", "private"]),
            "b_active": random.choice([True, False]),
            "n_click": random.randint(0, 1000),
            "t_event_date": (datetime.now() + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d") if content_type == "Eventi" else ""
        }
        
        # Aggiungi il contenuto alla lista dei contenuti
        contents.append(content)
        
        # Genera e aggiungi tag
        for _ in range(random.randint(1, 5)):  # Ogni contenuto avrà tra 1 e 5 tag
            tag = {
                "value": random.choice(tags),
                "content_id": str(content["_id"])  # Usa l'ID del contenuto
            }
            content_tags.append(tag)
        
        # Genera e aggiungi menzioni
        for _ in range(random.randint(1, 3)):  # Ogni contenuto avrà tra 1 e 3 menzioni
            mention = {
                "value": random.choice(all_aliases),
                "content_id": str(content["_id"])  # Usa l'ID del contenuto
            }
            content_mentions.append(mention)
        
        # Genera e aggiungi preferiti
        user = random.choice(users)
        booked = {
            "content_id": str(content["_id"]),
            "t_username": user["t_username"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        content_booked.append(booked)
        
        # Genera likes per il contenuto
        like_count = random.randint(1, 10)  # Numero casuale di like per ogni contenuto
        for _ in range(like_count):
            like_user = random.choice(users)
            content_like = {
                "content_id": str(content["_id"]),
                "t_username": like_user["t_username"],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            content_likes.append(content_like)
        
        # Genera commenti e risposte per ogni contenuto
        for _ in range(5):  # 5 commenti per ogni contenuto
            comment_user = random.choice(users)
            comment = {
                "content_id": str(content["_id"]),
                "parent_discussion_id": "",
                "body": f"Comment body {random_string(20)}",
                "like_count": random.randint(0, 5),  # Like count casuale per il commento
                "t_alias_generated": comment_user["t_username"],
                "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "t_alias_generated_reply": ""
            }
            content_discussions.append(comment)
            
            # Genera likes per il commento
            for _ in range(comment["like_count"]):
                like_user = random.choice(users)
                like = {
                    "content_id": str(content["_id"]),
                    "discussion_id": str(comment["_id"]),
                    "t_username": like_user["t_username"],
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                discussion_likes.append(like)
            
            # Genera risposte per ogni commento
            for _ in range(2):  # 2 risposte per ogni commento
                reply_user = random.choice(users)
                reply = {
                    "content_id": str(content["_id"]),
                    "parent_discussion_id": str(comment["_id"]),
                    "body": f"Reply body {random_string(20)}",
                    "like_count": random.randint(0, 5),  # Like count casuale per la risposta
                    "t_alias_generated": reply_user["t_username"],
                    "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "t_alias_generated_reply": comment["t_alias_generated"]
                }
                content_discussions.append(reply)
                
                # Genera likes per la risposta
                for _ in range(reply["like_count"]):
                    like_user = random.choice(users)
                    like = {
                        "content_id": str(content["_id"]),
                        "discussion_id": str(reply["_id"]),
                        "t_username": like_user["t_username"],
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    discussion_likes.append(like)
        
        # Genera e aggiungi location per gli eventi
        if content_type == "Eventi":
            event_location = {
                "event_id": str(content["_id"]),
                "t_address": f"{random_string(5)} Main St",
                "t_cap": random.randint(10000, 99999),
                "t_city": random.choice(cities),
                "t_location_name": random.choice(locations),
                "t_province": random.choice(provinces),
                "t_state": random.choice(states)
            }
            event_locations.append(event_location)
            
            # Genera e aggiungi mappe per gli eventi
            map_columns = random.randint(3, 10)
            map_rows = random.randint(3, 10)
            total_seats = map_columns * map_rows
            
            event_map = {
                "t_map_name": f"Map {random_string(5)}",
                "t_map_event_id": str(content["_id"]),
                "t_map_type": "DISCOTECA",
                "t_map_num_column": map_columns,
                "t_map_num_rows": map_rows,
                "t_map_total_seat": total_seats
            }
            event_maps.append(event_map)
            
            map_id = event_map["_id"]
            
            # Genera e aggiungi oggetti della mappa
            for _ in range(total_seats):
                x = random.randint(0, map_rows - 1)
                y = random.randint(0, map_columns - 1)
                width = random.randint(80, 240)
                height = random.randint(40, 100)
                min_person = random.randint(1, 5)
                max_person = random.randint(min_person, 10)
                limit_buy = random.randint(min_person, max_person)
                price = random.uniform(10, 100)
                is_acquistabile = random.choice([True, False])
                
                object_map = {
                    "n_id_map": map_id,
                    "n_min_num_person": min_person,
                    "n_max_num_person": max_person,
                    "n_limit_buy_for_person": limit_buy,
                    "n_object_price": price,
                    "n_obj_map_cord_x": x,
                    "n_obj_map_cord_y": y,
                    "n_obj_map_cord_z": 1,
                    "n_obj_map_width": width,
                    "n_obj_map_height": height,
                    "n_obj_map_text": f"Object {random_string(5)}",
                    "n_obj_map_fill": f"#{random.randint(0, 0xFFFFFF):06x}",
                    "t_note": "",
                    "t_type": {"TABLE": {"DISCOTECA": True}},
                    "is_acquistabile": is_acquistabile
                }
                object_maps.append(object_map)
                
                object_map_id = object_map["_id"]
                
                # Genera e aggiungi posti a sedere per ogni oggetto della mappa
                for seat_num in range(total_seats):
                    seat = {
                        "n_seat_num": seat_num,
                        "n_object_map_id": object_map_id,
                        "n_id_event": str(content["_id"]),
                        "is_sell": random.choice([True, False]),
                        "is_acquistabile": is_acquistabile
                    }
                    object_seats.append(seat)
            
            # Genera e aggiungi coupon per gli eventi
            for _ in range(5):  # 5 coupon per ogni evento
                coupon = {
                    "event_id": str(content["_id"]),
                    "coupon_code": f"COUPON{random_string(5).upper()}",
                    "discount": random.randint(1, 100)  # Sconto tra 1 e 100
                }
                event_coupons.append(coupon)
    
    # Inserisci i documenti nelle rispettive collezioni
    contents_collection.insert_many(contents)
    content_tags_collection.insert_many(content_tags)
    content_mentions_collection.insert_many(content_mentions)
    content_booked_collection.insert_many(content_booked)
    content_discussion_collection.insert_many(content_discussions)
    discussion_likes_collection.insert_many(discussion_likes)
    content_likes_collection.insert_many(content_likes)
    event_location_collection.insert_many(event_locations)
    event_maps_collection.insert_many(event_maps)
    object_maps_collection.insert_many(object_maps)
    object_seats_collection.insert_many(object_seats)
    event_coupons_collection.insert_many(event_coupons)
    
    print("Contenuti, tag, menzioni, preferiti, discussioni, like discussioni, like contenuti, location eventi, mappe eventi, oggetti mappe, posti a sedere e coupon eventi inseriti con successo.")

# Esegui lo script di inserimento
insert_contents()
