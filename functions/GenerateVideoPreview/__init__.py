import logging
import os
import io
import json
import cv2
import numpy as np
import tempfile
from azure.storage.blob import BlobServiceClient
import azure.functions as func

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)

def generate_preview(video_data: bytes) -> bytes:
    """Estrae il primo frame del video e lo converte in JPEG."""
    # Crea un file temporaneo per il video
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
        temp_video_file.write(video_data)
        temp_video_file_path = temp_video_file.name

    # Utilizza OpenCV per leggere il video
    cap = cv2.VideoCapture(temp_video_file_path)

    success, frame = cap.read()
    cap.release()

    if not success:
        raise ValueError("Non è stato possibile estrarre un frame dal video.")

    # Ridimensiona l'immagine per la preview
    frame = cv2.resize(frame, (128, 128))  # Dimensioni per la preview

    # Converti l'immagine in formato JPEG
    _, buffer = cv2.imencode('.jpg', frame)

    # Rimuove il file temporaneo
    os.remove(temp_video_file_path)

    return buffer.tobytes()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        try:
            # Retrieve the connection string and container name from environment variables
            connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')

            # Parse the request to get the file
            file = req.files.get('file')
            if not file:
                return func.HttpResponse(
                    "File non fornito.",
                    status_code=400
                )

            file_name = file.filename
            file_data = file.stream.read()

            # Generate a preview of the video
            preview_data = generate_preview(file_data)
            preview_file_name = f"preview_{file_name}.jpg"

            # Create a blob service client
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)

            # Upload the original video
            original_blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
            original_blob_client.upload_blob(file_data, overwrite=True)

            # Upload the preview image
            preview_blob_client = blob_service_client.get_blob_client(container=container_name, blob=preview_file_name)
            preview_blob_client.upload_blob(preview_data, overwrite=True)

            # Get URLs of the uploaded blobs
            original_blob_url = original_blob_client.url
            preview_blob_url = preview_blob_client.url

            return func.HttpResponse(
                body=json.dumps({
                    "message": "Video e preview caricati con successo.",
                    "original_url": original_blob_url,
                    "preview_url": preview_blob_url
                }),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse("Error processing file.", status_code=500)
    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )
