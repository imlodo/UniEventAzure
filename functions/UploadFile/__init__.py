import logging
import os
import json
import jwt
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import azure.functions as func

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        try:
            # Ottieni il token JWT dall'header Authorization
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    "Token non fornito o non valido.",
                    status_code=401
                )

            jwt_token = auth_header.split(' ')[1]
            secret_key = os.getenv('JWT_SECRET_KEY')

            try:
                decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    "Token scaduto.",
                    status_code=401
                )
            except jwt.InvalidTokenError:
                return func.HttpResponse(
                    "Token non valido.",
                    status_code=401
                )

            # Ottieni l'ID utente dal token decodificato
            t_username = decoded_token.get('username')
            if not t_username:
                return func.HttpResponse(
                    "Token non contiene un username valido.",
                    status_code=401
                )

            # Retrieve the connection string and container name from environment variables
            connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')

            # Parse the request to get the file
            file = req.files['file']
            file_name = file.filename
            file_data = file.stream.read()

            # Create a blob client using the local file name as the name for the blob
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

            # Upload the file to Azure Blob Storage
            blob_client.upload_blob(file_data, overwrite=True)

            # Get the URL of the uploaded blob
            blob_url = blob_client.url

            return func.HttpResponse(
                body=json.dumps({"message": f"File {file_name} uploaded successfully.", "url": blob_url}),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Error uploading file.", status_code=500)
    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )
