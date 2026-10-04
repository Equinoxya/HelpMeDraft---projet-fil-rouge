# backend/app/services/auth_service.py
import datetime
import hashlib
import re
import secrets

import bcrypt
import jwt
from flask import current_app
from sqlalchemy import delete, select

from database.db import SessionLocal, UserSession
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
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": user_id,  # UUID string, pas un int
        "iat": now,
        "exp": now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
    # `from e` conserve l'exception d'origine dans la chaîne (__cause__) : le
    # message reste celui qu'attend l'appelant, mais la trace garde de quoi
    # diagnostiquer. Sans elle, Python signale « During handling of the above
    # exception, another exception occurred », ce qui brouille la lecture.
    except jwt.ExpiredSignatureError as e:
        raise ValueError("Token expiré") from e
    except jwt.InvalidTokenError as e:
        raise ValueError("Token invalide") from e


# ── Refresh token (empreinte stockée en base dans UserSession) ───────────────
# SÉCURITÉ : le jeton en clair ne quitte jamais le couple serveur -> cookie du
# client. En base on ne garde que son empreinte SHA-256, comme pour les jetons
# de réinitialisation de mot de passe. Conséquence : une fuite de la table
# user_session (dump, injection SQL, sauvegarde mal protégée) ne permet plus de
# rejouer les sessions actives, car l'empreinte n'est pas inversible.
# SHA-256 sans sel suffit ici — contrairement à un mot de passe, le jeton est
# aléatoire sur 64 octets, donc non attaquable par dictionnaire.
def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(plain_token: str) -> str:
    return hashlib.sha256(plain_token.encode()).hexdigest()


def purge_expired_sessions(user_id: str | None = None) -> int:
    """
    Supprime les sessions dont la date d'expiration est passée, et rend le
    nombre de lignes supprimées.

    Couvre les deux cas d'accumulation de la table `user_session` :
      - les sessions jamais fermées, dont le jeton a expiré au bout de 7 jours ;
      - les sessions révoquées par la rotation, qui restent volontairement en
        base pour permettre la détection de rejeu.

    Le critère est l'expiration et NON le drapeau `revoke` : une session
    révoquée doit survivre jusqu'au terme de son jeton, sinon un jeton volé
    puis rejoué ne serait plus reconnu comme un rejeu — il serait simplement
    « inconnu », et la détection de vol tomberait.

    Avec user_id, ne purge que ce compte ; sans, purge toute la table (usage
    prévu : tâche planifiée).
    """
    with SessionLocal() as db_session:
        stmt = delete(UserSession).where(UserSession.refresh_token_exp < utc_now_naive())
        if user_id is not None:
            stmt = stmt.where(UserSession.user_id == user_id)
        supprimees = db_session.execute(stmt).rowcount
        db_session.commit()
        return supprimees or 0


def create_session(user_id: str) -> str:
    # Purge opportuniste : la connexion est le moment naturel pour nettoyer
    # les sessions mortes de ce compte, sans tâche planifiée ni travail
    # supplémentaire sur le chemin critique des autres requêtes.
    purge_expired_sessions(user_id)

    refresh_token = generate_refresh_token()
    with SessionLocal() as db_session:
        user_session = UserSession(
            user_id=user_id,
            refresh_token_hash=hash_refresh_token(refresh_token),
            refresh_token_exp=utc_now_naive() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
        )
        db_session.add(user_session)
        db_session.commit()
    # Seul l'appelant (la route) reçoit le jeton en clair, pour le cookie.
    return refresh_token


def verify_refresh_token(refresh_token: str) -> str:
    token_hash = hash_refresh_token(refresh_token)
    with SessionLocal() as db_session:
        stmt = select(UserSession).where(UserSession.refresh_token_hash == token_hash)
        session = db_session.execute(stmt).scalar_one_or_none()
        if session is None:
            raise ValueError("Refresh token invalide")
        # Une session révoquée reste en base jusqu'à l'expiration de son jeton,
        # pour permettre la détection de rejeu (cf. rotate_refresh_token). Elle
        # ne doit donc jamais être acceptée comme valide ici.
        if session.revoke:
            raise ValueError("Refresh token révoqué")
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
    old_token_hash = hash_refresh_token(old_refresh_token)
    with SessionLocal() as db_session:
        stmt = select(UserSession).where(UserSession.refresh_token_hash == old_token_hash)
        session = db_session.execute(stmt).scalar_one_or_none()

        if session is None:
            raise ValueError("Refresh token invalide")

        if session.revoke:
            revoke_all_user_sessions(session.user_id, db_session)
            db_session.commit()
            raise ValueError("Réutilisation détectée : toutes les sessions ont été révoquées")

        if session.refresh_token_exp < utc_now_naive():
            db_session.delete(session)
            db_session.commit()
            raise ValueError("Refresh token expiré")

        session.revoke = True

        new_refresh_token = generate_refresh_token()
        new_session = UserSession(
            user_id=session.user_id,
            refresh_token_hash=hash_refresh_token(new_refresh_token),
            refresh_token_exp=utc_now_naive() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
        )
        db_session.add(new_session)
        db_session.commit()

        return session.user_id, new_refresh_token


def generate_reset_token() -> tuple[str, str]:
    plain_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
    return plain_token, token_hash


def hash_reset_token(plain_token: str) -> str:
    return hashlib.sha256(plain_token.encode()).hexdigest()


def is_reset_token_expired(expires_at: datetime.datetime) -> bool:
    return utc_now_naive() > expires_at  # réutilise ton helper existant
