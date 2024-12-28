from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from .config import settings
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer

passwd_context = CryptContext(
    schemes=['bcrypt']
)

ACCESS_TOKEN_EXPIRE = 3600

def generate_passwd_hash(password:str) -> str:
    return passwd_context.hash(password)

def verify_passwd_hash(password:str, hashed_password:str) -> bool:
    return passwd_context.verify(password, hashed_password)

def create_access_token(user_data:dict, expiry:timedelta = None, refresh:bool = False):
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRE))
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM 
    )

    return token

def decode_token(token:str):

    try:
        token_data = jwt.decode(
            jwt=token,
            algorithms=settings.ALGORITHM,
            key=settings.SECRET_KEY,
        )

        return token_data
    except jwt.PyJWKError as e:
        logging.exception(e)
        return None

def create_safe_url(user_uid: str, email: str) -> str:
    signage = {
        'user_uid': user_uid,
        'email': email
    }
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt='email-verification')
    return serializer.dumps(signage)

def decode_safe_url(url:str) -> dict:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt='email-verification')
    return serializer.loads(url, max_age=3600)