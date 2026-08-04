# backend/app/services/auth_service.py
import bcrypt
import jwt
import datetime
import secrets
import hashlib
import re
from flask import current_app
from sqlalchemy import select
from database.db import SessionLocal, User, UserSession
from utilitaires import utc_now_naive

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

def is_password_valid(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


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
            refresh_token_exp=utc_now_naive()
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
        if session.refresh_token_exp < utc_now_naive():
            db_session.delete(session)
            db_session.commit()
            raise ValueError("Refresh token expiré")
        return session.user_id
    
def revoke_all_user_sessions(user_id: str, db_session) -> None:
    stmt = select(UserSession).where(UserSession.user_id == user_id)
    sessions = db_session.execute(stmt).scalars().all()
    for session in sessions:
        db_session.delete(session)


def rotate_refresh_token(old_refresh_token: str) -> tuple[str, str]:
    """
    Vérifie le refresh token présenté, applique la rotation, et détecte
    une éventuelle réutilisation frauduleuse.
    Retourne (user_id, nouveau_refresh_token).
    Lève ValueError si le token est invalide, expiré, ou réutilisé.
    """
    with SessionLocal() as db_session:
        stmt = select(UserSession).where(UserSession.refresh_token == old_refresh_token)
        session = db_session.execute(stmt).scalar_one_or_none()

        if session is None:
            raise ValueError("Refresh token invalide")

        if session.revoked:
            revoke_all_user_sessions(session.user_id, db_session)
            db_session.commit()
            raise ValueError("Réutilisation détectée : toutes les sessions ont été révoquées")

        if session.refresh_token_exp < utc_now_naive():
            db_session.delete(session)
            db_session.commit()
            raise ValueError("Refresh token expiré")

        session.revoked = True

        new_refresh_token = generate_refresh_token()
        new_session = UserSession(
            user_id=session.user_id,
            refresh_token=new_refresh_token,
            refresh_token_exp=utc_now_naive() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
        )
        db_session.add(new_session)
        db_session.commit()

        return session.user_id, new_refresh_token

def generate_reset_token() -> tuple[str,str]:
    plain_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
    return plain_token, token_hash

def hash_reset_token(plain_token: str) -> str:
    return hashlib.sha256(plain_token.encode()).hexdigest()

def is_reset_token_expired(expires_at: datetime) -> bool:
    return utc_now_naive() > expires_at  # réutilise ton helper existant

