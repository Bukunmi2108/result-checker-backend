from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from .config import settings
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent

mail_config = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_STARTTLS = settings.MAIL_STARTTLS,
    MAIL_SSL_TLS = settings.MAIL_SSL_TLS,
    MAIL_FROM = settings.MAIL_FROM, 
    MAIL_FROM_NAME = settings.MAIL_FROM_NAME,
    USE_CREDENTIALS = settings.USE_CREDENTIALS,
    VALIDATE_CERTS = settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER = Path(BASE_DIR, 'templates')
)

mail = FastMail(
    config=mail_config
)


def create_message(recipients:List[str], subject: str, body:str):
    try:
    
        message = MessageSchema(
            recipients= recipients,
            subject=subject,
            body=body, 
            subtype=MessageType.html
        )

        return message
    except Exception as e:
        print(e)