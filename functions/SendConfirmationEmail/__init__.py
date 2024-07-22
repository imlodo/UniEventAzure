import logging
import os
import json
from pymongo import MongoClient
import azure.functions as func
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import datetime, timedelta
import jwt

# Carica le variabili di ambiente
load_dotenv()

# Ottieni le stringhe di connessione e le credenziali GMAIL
connect_string = os.getenv("DB_CONNECTION_STRING")
gmail_user = os.getenv("GMAIL_USER")
gmail_password = os.getenv("GMAIL_PASSWORD")
jwt_secret_key = os.getenv("JWT_SECRET_KEY")

client = MongoClient(connect_string)
db = client.unieventmongodb
users_collection = db.Users

def generate_jwt_token(username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, jwt_secret_key, algorithm='HS256')

def send_confirmation_email(email, token):
    logging.error(gmail_user)
    logging.error(gmail_password)
    confirmation_url = f"{os.getenv('RESET_PASSWORD_URL')}?token={token}"
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = email
    msg['Subject'] = 'Password Reset Confirmation'
    body = f'<p>Click the link to reset your password: <a href="{confirmation_url}">Reset Password</a></p>'
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, email, text)
        server.quit()
        return func.HttpResponse("Confirmation email sent", status_code=200)
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return func.HttpResponse("Failed to send confirmation email", status_code=500)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        username = req_body.get('username')

        if not username:
            return func.HttpResponse("Username is required.", status_code=400)

        user = users_collection.find_one({"t_username": username})
        if not user:
            return func.HttpResponse("User not found.", status_code=404)

        email = user.get('t_email')
        if not email:
            return func.HttpResponse("User does not have an email address.", status_code=400)

        token = generate_jwt_token(username)
        send_confirmation_email(email, token)

        response_body = json.dumps(
            {"message": "Se l'account è censito nei nostri sistemi, riceverai una email contenente un link per confermare il reset pw"})
        return func.HttpResponse(
            body=response_body,
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return func.HttpResponse("An error occurred while sending the confirmation email.", status_code=500)
