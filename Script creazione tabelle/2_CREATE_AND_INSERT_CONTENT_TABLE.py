import os
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import string
from dotenv import load_dotenv

load_dotenv()

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
users_collection = db.Users

# Dati di esempio per i topics e gli eventi
topics_aliases = ["davidestrianese", "mariobaldi", "francescoferrara"]
events_aliases = ["chiaraferragni", "salmo", "discosalerno", "discominori"]
all_aliases = topics_aliases + events_aliases
tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
cities = ["Rome", "Milan", "Naples", "Turin", "Palermo"]
provinces = ["RM", "MI", "NA", "TO", "PA"]
states = ["Italy"]
locations = ["Stadium", "Concert Hall", "Theater", "Club", "Arena"]

# Funzione per generare una stringa casuale
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Recupera tutti gli utenti dal database
users = list(users_collection.find({}))

# Funzione per ottenere una data casuale
def random_date(days_range=365):
    return (datetime.now() + timedelta(days=random.randint(0, days_range))).strftime("%Y-%m-%d")

def insert_contents(batch_size=10):
    contents = []
    group_id = 1

    for i in range(batch_size):
        if i % 3 == 0:
            group_id += 1
        content_type = "Topics" if i < batch_size / 2 else "Eventi"
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
            "t_event_date": random_date() if content_type == "Eventi" else ""
        }
        contents.append(content)

    # Inserisci i contenuti e ottieni gli ID generati
    inserted_contents = contents_collection.insert_many(contents)
    content_ids = inserted_contents.inserted_ids
    return content_ids

def insert_related_data(content_ids):
    content_tags = []
    content_mentions = []
    content_booked = []
    content_likes = []
    discussion_likes = []

    for content_id in content_ids:
        content = contents_collection.find_one({"_id": content_id})

        # Genera e aggiungi tag
        for _ in range(random.randint(1, 5)):
            tag = {"value": random.choice(tags), "content_id": content_id}
            content_tags.append(tag)

        # Genera e aggiungi menzioni
        for _ in range(random.randint(1, 3)):
            mention = {"value": random.choice(all_aliases), "content_id": content_id}
            content_mentions.append(mention)

        # Genera e aggiungi preferiti
        user = random.choice(users)
        booked = {"content_id": content_id, "t_username": user["t_username"], "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        content_booked.append(booked)

        # Genera likes per il contenuto
        like_count = random.randint(1, 10)
        for _ in range(like_count):
            like_user = random.choice(users)
            content_like = {"content_id": content_id, "t_username": like_user["t_username"], "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            content_likes.append(content_like)

    content_tags_collection.insert_many(content_tags)
    content_mentions_collection.insert_many(content_mentions)
    content_booked_collection.insert_many(content_booked)
    content_likes_collection.insert_many(content_likes)

    # Inserisci discussioni e like per le discussioni
    insert_discussions(content_ids)

def insert_discussions(content_ids):
    content_discussions = []
    discussion_likes = []

    for content_id in content_ids:
        for _ in range(5):
            comment_user = random.choice(users)
            comment = {
                "content_id": content_id,
                "parent_discussion_id": "",
                "body": f"Comment body {random_string(20)}",
                "like_count": random.randint(0, 5),
                "t_alias_generated": comment_user["t_username"],
                "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "t_alias_generated_reply": ""
            }
            content_discussion_collection.insert_one(comment)
            comment_id = comment["_id"]

            for _ in range(comment["like_count"]):
                like_user = random.choice(users)
                like = {"content_id": content_id, "discussion_id": comment_id, "t_username": like_user["t_username"], "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                discussion_likes.append(like)

            for _ in range(2):
                reply_user = random.choice(users)
                reply = {
                    "content_id": content_id,
                    "parent_discussion_id": comment_id,
                    "body": f"Reply body {random_string(20)}",
                    "like_count": random.randint(0, 5),
                    "t_alias_generated": reply_user["t_username"],
                    "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "t_alias_generated_reply": comment["t_alias_generated"]
                }
                content_discussion_collection.insert_one(reply)
                reply_id = reply["_id"]

                for _ in range(reply["like_count"]):
                    like_user = random.choice(users)
                    like = {"content_id": content_id, "discussion_id": reply_id, "t_username": like_user["t_username"], "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    discussion_likes.append(like)

    discussion_likes_collection.insert_many(discussion_likes)

def insert_event_data(content_ids):
    event_locations = []
    event_maps = []
    object_seats = []
    event_coupons = []

    for content_id in content_ids:
        content = contents_collection.find_one({"_id": content_id})

        if content["t_type"] == "Eventi":
            event_location = {
                "event_id": content_id,
                "t_address": f"{random_string(5)} Main St",
                "t_cap": random.randint(10000, 99999),
                "t_city": random.choice(cities),
                "t_location_name": random.choice(locations),
                "t_province": random.choice(provinces),
                "t_state": random.choice(states)
            }
            event_locations.append(event_location)

            map_columns = random.randint(3, 10)
            map_rows = random.randint(3, 10)
            total_seats = map_columns * map_rows

            event_map = {
                "t_map_name": f"Map {random_string(5)}",
                "t_map_event_id": content_id,
                "t_map_type": "DISCOTECA",
                "t_map_num_column": map_columns,
                "t_map_num_rows": map_rows,
                "t_map_total_seat": total_seats
            }
            event_maps_collection.insert_one(event_map)
            map_id = event_map["_id"]

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
                object_maps_collection.insert_one(object_map)
                object_map_id = object_map["_id"]

                for seat_num in range(total_seats):
                    seat = {
                        "n_seat_num": seat_num,
                        "n_object_map_id": object_map_id,
                        "n_id_event": content_id,
                        "is_sell": random.choice([True, False]),
                        "is_acquistabile": is_acquistabile
                    }
                    object_seats.append(seat)

            for _ in range(5):
                coupon = {
                    "event_id": content_id,
                    "coupon_code": f"COUPON{random_string(5).upper()}",
                    "discount": random.randint(1, 100)
                }
                event_coupons.append(coupon)

    event_location_collection.insert_many(event_locations)
    object_seats_collection.insert_many(object_seats)
    event_coupons_collection.insert_many(event_coupons)

def main():
    batch_size = 30  # Numero di contenuti da inserire in ogni batch
    content_ids = insert_contents(batch_size)
    insert_related_data(content_ids)
    insert_event_data(content_ids)
    print("Dati inseriti con successo.")

if __name__ == "__main__":
    main()
