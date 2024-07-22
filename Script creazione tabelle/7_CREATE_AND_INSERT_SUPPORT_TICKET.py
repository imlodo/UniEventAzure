import os
import pymongo
import random
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
# Connessione al database MongoDB
connectString = os.getenv("DB_CONNECTION_STRING")
client = MongoClient(connectString)

# Seleziona il database e le collezioni
db = client.unieventmongodb
users_collection = db.Users
support_tickets_collection = db.SupportTickets
support_ticket_discussion_collection = db.SupportTicketDiscussion

# Funzione per creare ticket di supporto
def create_support_tickets_and_discussions():
    # Recupera utenti con ruolo "Utente"
    users = list(users_collection.find({"t_role": "Utente"}))
    
    if len(users) < 5:
        print("Non ci sono abbastanza utenti con il ruolo 'Utente' per creare 5 ticket.")
        return

    # Recupera utenti con ruolo "Moderatore" o "Super Moderatore" per le risposte
    moderators_or_super_mods = list(users_collection.find({"t_role": {"$in": ["Moderatore", "Super Moderatore"]}}))
    
    if not moderators_or_super_mods:
        print("Nessun moderatore o super moderatore trovato.")
        return

    # Crea almeno 5 ticket di supporto
    for i in range(5):
        user = random.choice(users)
        t_username = user.get("t_username")
        t_alias_generated = user.get("t_alias_generated")

        # Crea il ticket di supporto
        expired_date = datetime.utcnow() + timedelta(days=30)  # Ticket valido per 30 giorni
        description = f"Richiesta di supporto da {t_username}"
        
        support_ticket_record = {
            "t_username": t_username,
            "description": description,
            "status": "Aperto",
            "expired_date": expired_date,
            "isScaduto": False
        }
        result = support_tickets_collection.insert_one(support_ticket_record)
        support_ticket_id = result.inserted_id

        print(f"Ticket di supporto creato: {support_ticket_record}")

        # Crea la discussione di supporto
        if moderators_or_super_mods:
            moderator = random.choice(moderators_or_super_mods)
            mod_username = moderator.get("t_username")
            mod_role = moderator.get("t_role")

            support_ticket_discussion_record = {
                "support_ticket_id": support_ticket_id,
                "alias": t_alias_generated,
                "role": mod_role,
                "replyDateHour": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "body": description,
                "attachments": []  # Lista vuota di allegati
            }
            support_ticket_discussion_collection.insert_one(support_ticket_discussion_record)
            
            print(f"Discussione di supporto creata: {support_ticket_discussion_record}")

create_support_tickets_and_discussions()
