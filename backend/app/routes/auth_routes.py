import os
from datetime import timedelta
from functools import wraps

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import select

from app.extension import limiter, mail
from app.services.auth_service import (
    create_session,
    decode_access_token,
    generate_access_token,
    generate_reset_token,
    hash_password,
    hash_refresh_token,
    hash_reset_token,
    is_password_valid,
    is_reset_token_expired,
    rotate_refresh_token,
    verify_password,
)
from app.services.email_service import send_reset_password_email
from database.db import Consentement, PasswordReset, SessionLocal, User, UserSession
from utilitaires import utc_now_naive

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 jours


def set_refresh_cookie(response, refresh_token: str):
    """
    Pose le cookie de refresh de façon homogène sur toutes les routes.
    - httponly : le cookie est invisible pour JavaScript, donc un XSS ne peut
      pas exfiltrer le jeton de session longue durée.
    - secure : piloté par APP_ENV (False en dev sur http://localhost, True
      partout ailleurs) pour que le jeton ne puisse pas transiter en clair.
    - path=/auth : le cookie n'est envoyé qu'aux routes d'authentification,
      ce qui réduit la surface exposée (et le CSRF au seul /auth/refresh).
    - samesite=Strict : protection CSRF. Le refresh token étant dans un cookie,
      le navigateur le joindrait automatiquement à une requête POST déclenchée
      depuis un site tiers vers /auth/refresh. L'attaquant ne lit pas la réponse
      (le CORS ne l'autorise pas), mais l'effet de bord se produit : la route
      applique une ROTATION, donc la requête forgée invalide le jeton légitime
      de la victime, et le rejeu suivant par le vrai front est interprété comme
      une réutilisation frauduleuse -> toutes ses sessions sont révoquées. Le
      résultat est un déni de service sur le compte.
      "Lax" bloque déjà les POST cross-site ; "Strict" ferme en plus les
      navigations top-level. CONTRAINTE DE DÉPLOIEMENT : le cookie n'est envoyé
      que si le front et l'API sont sur le même site (au sens eTLD+1). En dev
      les deux sont sur localhost, donc même site malgré les ports 5173 et 5000.
      En production, il faut deux sous-domaines d'un même domaine, ou l'API
      derrière un reverse proxy sur le domaine du front.
      Les autres routes ne sont pas concernées : elles s'authentifient par
      en-tête Authorization: Bearer, que le navigateur n'ajoute jamais tout
      seul — un formulaire tiers ne peut donc pas les appeler au nom du client.
    """
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=current_app.config["COOKIE_SECURE"],
        samesite="Strict",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/auth",
    )
    return response


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("3 per hour")
def register():
    data = request.get_json()
    requiered_fields = ["email", "mdp", "lastname", "firstname", "rgpd_consent"]
    for field in requiered_fields:
        if not data.get(field):
            return jsonify({"error": f"Le champ {field} est requis"}), 400

    if data.get("rgpd_consent") is not True:
        return jsonify({"error": "Le consentement RGPD est requis"}), 400

    email = data["email"]
    plain_password = data["mdp"]

    if not is_password_valid(plain_password):
        return jsonify(
            {
                "error": "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre"
            }
        ), 400

    with SessionLocal() as db_session:
        stmt = select(User).where(User.email == email)
        existing_user = db_session.execute(stmt).scalar_one_or_none()
        if existing_user is not None:
            return jsonify({"error": "Cet email est déjà utilisé"}), 409

        new_user = User(
            email=email,
            mdp_hash=hash_password(plain_password),
            lastname=data["lastname"],
            firstname=data["firstname"],
            role="user",
        )
        db_session.add(new_user)
        db_session.flush()  # génère user_id (via gen_uuid) sans commit définitif

        consentement = Consentement(
            type_consentement="rgpd",
            accepte=True,
            user_id=new_user.user_id,
        )
        db_session.add(consentement)

        db_session.commit()
        db_session.refresh(new_user)

        return jsonify(
            {
                "message": "Utilisateur créé avec succès",
                "user_id": new_user.user_id,
                "email": new_user.email,
            }
        ), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    if not data.get("email") or not data.get("mdp"):
        return jsonify({"error": "Email ou mot de passe requis"}), 400
    email = data["email"]
    plain_password = data["mdp"]

    with SessionLocal() as db_session:
        stmt = select(User).where(User.email == email)
        user = db_session.execute(stmt).scalar_one_or_none()
        if user is None or not verify_password(plain_password, user.mdp_hash):
            return jsonify({"error": "Email ou mot de passe incorrect"}), 401
        access_token = generate_access_token(user.user_id)
        refresh_token = create_session(user.user_id)

        response = jsonify(
            {
                "access_token": access_token,
                "user": {
                    "id": user.user_id,
                    "email": user.email,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "role": user.role,
                },
            }
        )
        set_refresh_cookie(response, refresh_token)
        return response, 200


@auth_bp.route("/refresh", methods=["POST"])
# Le jeton de rafraîchissement fait 64 octets tirés au hasard : le deviner par
# force brute est hors de portée, cette limite ne protège donc pas le secret.
# Elle borne l'usage de la route — épuisement de ressources côté serveur, et
# martèlement automatisé si un cookie fuit. 30 par minute laisse largement
# passer un usage normal : un rafraîchissement toutes les 15 minutes par
# session, même avec plusieurs onglets ou appareils derrière une même IP.
@limiter.limit("30 per minute")
def refresh():
    token = request.cookies.get("refresh_token")
    if not token:
        return jsonify({"error": "Aucun token"}), 401

    try:
        user_id, new_refresh_token = rotate_refresh_token(token)
    except ValueError as e:
        response = jsonify({"error": str(e)})
        response.delete_cookie("refresh_token", path="/auth")
        return response, 401
    new_access_token = generate_access_token(user_id)

    response = jsonify({"access_token": new_access_token})
    set_refresh_cookie(response, new_refresh_token)
    return response, 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get("refresh_token")
    if not token:
        return jsonify({"error": "Aucune session active"}), 400
    with SessionLocal() as db_session:
        # La base ne contient que l'empreinte : on hache le jeton du cookie
        # pour retrouver la session à supprimer.
        stmt = select(UserSession).where(
            UserSession.refresh_token_hash == hash_refresh_token(token)
        )
        session = db_session.execute(stmt).scalar_one_or_none()
        if session is not None:
            db_session.delete(session)
            db_session.commit()
    response = jsonify({"message": "Déconnexion réussite"})
    response.delete_cookie("refresh_token", path="/auth")
    return response, 200


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = decode_access_token(token)
        except Exception:
            return jsonify({"error": "Token invalide ou expiré"}), 401
        request.user_id = payload["sub"]  # adapte "sub" au nom réel de la claim dans ton JWT
        return f(*args, **kwargs)

    return decorated


@auth_bp.route("/me", methods=["GET"])
@token_required
def me():
    with SessionLocal() as db_session:
        stmt = select(User).where(User.user_id == request.user_id)
        user = db_session.execute(stmt).scalar_one_or_none()
        if user is None:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        return jsonify(
            {
                "id": user.user_id,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "role": user.role,
            }
        ), 200


# ==========================================RESET PASSWORD====================================================
@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("3 per hour")
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email requis"}), 400

    with SessionLocal() as db_session:
        stmt = select(User).where(User.email == email)
        user = db_session.execute(stmt).scalar_one_or_none()

        # Important : on répond pareil que l'utilisateur existe ou non,
        # pour ne pas révéler quels emails sont enregistrés (énumération de comptes)
        if user is not None:
            plain_token, token_hash = generate_reset_token()

            reset_entry = PasswordReset(
                user_id=user.user_id,
                token_hash=token_hash,
                expires_at=utc_now_naive() + timedelta(hours=1),
            )
            db_session.add(reset_entry)
            db_session.commit()

            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            reset_link = f"{frontend_url}/reset-password?token={plain_token}"
            # adapte au chemin réel de ton objet Mail
            send_reset_password_email(mail, user.email, user.firstname, reset_link)

        return jsonify(
            {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}
        ), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("mdp")

    if not token or not new_password:
        return jsonify({"error": "Token et nouveau mot de passe requis"}), 400

    if not is_password_valid(new_password):
        return jsonify(
            {
                "error": "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre"
            }
        ), 400

    token_hash = hash_reset_token(token)

    with SessionLocal() as db_session:
        stmt = select(PasswordReset).where(
            PasswordReset.token_hash == token_hash,
            # .is_(False) et non « not ... » : on construit ici une expression
            # SQL, pas une condition Python. La correction que suggère Ruff
            # (E712) évaluerait la véracité de l'objet colonne et produirait une
            # requête fausse.
            PasswordReset.used.is_(False),
        )
        reset_entry = db_session.execute(stmt).scalar_one_or_none()

        if reset_entry is None or is_reset_token_expired(reset_entry.expires_at):
            return jsonify({"error": "Lien invalide ou expiré"}), 400

        stmt_user = select(User).where(User.user_id == reset_entry.user_id)
        user = db_session.execute(stmt_user).scalar_one_or_none()
        if user is None:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        user.mdp_hash = hash_password(new_password)
        reset_entry.used = True
        stmt_session = select(UserSession).where(UserSession.user_id == user.user_id)
        sessions = db_session.execute(stmt_session).scalars().all()
        for session in sessions:
            db_session.delete(session)

        db_session.commit()

        return jsonify({"message": "Mot de passe réinitialisé avec succès"}), 200
