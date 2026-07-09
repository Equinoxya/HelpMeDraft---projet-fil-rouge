import bcrypt
import jwt
import datetime
from flask import current_app
#Hash
def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)
#Token
ACCESS_TOKEN_EXPIRES_MINUTES = 15

def generate_access_token(user_id: int) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub" : str(user_id),
        "iat" : now,
        "exp": now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        }
    token = jwt.decode(
        token,
        current_app.config['JWT_SECRET_KEY'],
        algorithms=['HS256']
    )
    return token

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError('Token expiré')
    except jwt.InvalidTokenError:
        raise ValueError('Token invalide')