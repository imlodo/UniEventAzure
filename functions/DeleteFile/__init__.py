import logging
import os
import json
import jwt
from azure.storage.blob import BlobServiceClient
import azure.functions as func

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'DELETE':
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

            # Parse the request to get the blob URL
            req_body = req.get_json()
            blob_url = req_body.get('blob_url')
            if not blob_url:
                return func.HttpResponse(
                    "blob_url non fornito nel corpo della richiesta.",
                    status_code=400
                )

            # Create a blob service client
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)

            # Extract the blob name from the URL
            blob_name = blob_url.split('/')[-1]
            print(blob_name)
            # Get a blob client
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

            # Delete the blob
            blob_client.delete_blob()

            return func.HttpResponse(
                body=json.dumps({"message": f"File {blob_name} deleted successfully."}),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(f"Error deleting file: {str(e)}", status_code=500)
    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo DELETE.",
            status_code=405
        )
