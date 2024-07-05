import logging
import os
import json
import random
import string
from pymongo import MongoClient
import azure.functions as func
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import jwt
from werkzeug.security import generate_password_hash

# Carica le variabili di ambiente
load_dotenv()

# Ottieni le stringhe di connessione e la chiave API da SendGrid
connect_string = os.getenv("DB_CONNECTION_STRING")
gmail_user = os.getenv("GMAIL_USER")
gmail_password = os.getenv("GMAIL_PASSWORD")
jwt_secret_key = os.getenv("JWT_SECRET_KEY")
email_from = os.getenv("EMAIL_FROM")

client = MongoClient(connect_string)
db = client.unieventmongodb
users_collection = db.Users


def generate_new_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    new_password = ''.join(random.choice(characters) for i in range(length))
    return new_password


def send_reset_password_email(email, new_password):
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = email
    msg['Subject'] = 'Your New Password'
    
    body = f'<p>Your new password is: {new_password}</p>'
    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, email, text)
        server.quit()
        return func.HttpResponse("Password reset and email sent", status_code=200)
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return func.HttpResponse("Failed to send new password email", status_code=500)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        token = req.params.get('token')
        if not token:
            return func.HttpResponse("Token is missing.", status_code=400)

        try:
            decoded_token = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return func.HttpResponse("Token has expired.", status_code=401)
        except jwt.InvalidTokenError:
            return func.HttpResponse("Invalid token.", status_code=401)

        username = decoded_token.get('username')
        if not username:
            return func.HttpResponse("Token does not contain a valid username.", status_code=401)

        # user = users_collection.find_one({"t_username": username})
        # if not user:
        #     return func.HttpResponse("User not found.", status_code=404)

        new_password = generate_new_password()
        hashed_password = generate_password_hash(new_password)

        # users_collection.update_one(
        #     {"t_username": username},
        #     {"$set": {"t_password": hashed_password}}
        # )

        # email = user['t_email']
        email = "anoloc@live.it"
        send_reset_password_email(email, new_password)
        response_body = json.dumps(
            {"message": "Password resettata correttamente. Verifica la tua email per la nuova password."})
        return func.HttpResponse(
            body=response_body,
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return func.HttpResponse("An error occurred while resetting the password.", status_code=500)
