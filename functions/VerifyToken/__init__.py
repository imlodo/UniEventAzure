import logging
import os
import jwt
import azure.functions as func

# Setup del logger per l'Azure Function
logging.basicConfig(level=logging.INFO)


# Funzione principale dell'Azure Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        try:
            auth_header = req.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return func.HttpResponse(
                    "Token non fornito o non valido.",
                    status_code=401
                )

            jwt_token = auth_header.split(' ')[1]
            secret_key = os.environ.get('JWT_SECRET_KEY',
                                        '96883c431142be979c69509655c4eca623a34714f948206b0cfbed0e986b173e')

            try:
                jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
                return func.HttpResponse(
                    "Token valido.",
                    status_code=200
                )
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

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return func.HttpResponse(
                "Si è verificato un errore durante la verifica del token.",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Metodo non supportato. Utilizzare il metodo POST.",
            status_code=405
        )
