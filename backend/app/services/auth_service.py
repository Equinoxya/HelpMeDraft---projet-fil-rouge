# backend/app/services/auth_service.py
import bcrypt
import jwt
import datetime
import secrets
from flask import current_app
from sqlalchemy import select
from database.db import SessionLocal, User, UserSession

ACCESS_TOKEN_EXPIRES_MINUTES = 15
REFRESH_TOKEN_EXPIRES_DAYS = 7


# ── Mot de passe ──────────────────────────────────────────────
def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ── Access token (JWT) ───────────────────────────────────────
def generate_access_token(user_id: str) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": user_id,  # UUID string, pas un int
        "iat": now,
        "exp": now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expiré")
    except jwt.InvalidTokenError:
        raise ValueError("Token invalide")


# ── Refresh token (stocké en base dans UserSession) ──────────
def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def create_session(user_id: str) -> str:
    refresh_token = generate_refresh_token()
    with SessionLocal() as db_session:
        user_session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            refresh_token_exp=datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
        )
        db_session.add(user_session)
        db_session.commit()
    return refresh_token


def verify_refresh_token(refresh_token: str) -> str:
    with SessionLocal() as db_session:
        stmt = select(UserSession).where(UserSession.refresh_token == refresh_token)
        session = db_session.execute(stmt).scalar_one_or_none()
        if session is None:
            raise ValueError("Refresh token invalide")
        if session.refresh_token_exp < datetime.datetime.now(datetime.timezone.utc):
            db_session.delete(session)
            db_session.commit()
            raise ValueError("Refresh token expiré")
        return session.user_id