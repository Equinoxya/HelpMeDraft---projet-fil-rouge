from flask import Blueprint, jsonify, request
from database.db import SessionLocal, User, UserSession, Consentement
from app.services.auth_service import hash_password, verify_password, generate_access_token, create_session, verify_refresh_token, generate_refresh_token
from sqlalchemy import select

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
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

        return jsonify({
            "message": "Utilisateur créé avec succès",
            "user_id": new_user.user_id,
            "email": new_user.email,
        }), 201
        
@auth_bp.route("/login", methods= ["POST"])
def login():
    data = request.get_json()
    if not data.get("email") or not data.get("mdp"):
        print("RAW:", repr(request.data))
        print("PARSED:", data)
        return jsonify({"error" : "Email ou mot de passe requis"}), 400
    email = data["email"]
    plain_password = data["mdp"]
    with SessionLocal() as db_session:
        stmt = select(User). where(User.email == email)
        user = db_session.execute(stmt).scalar_one_or_none()
        if user is None or not verify_password(plain_password, user.mdp_hash):
            return jsonify({"error" : "Email ou mot de passe incorrect"}), 401
        access_token = generate_access_token(user.user_id)
        refresh_token = create_session(user.user_id)
        
        response = jsonify({
        "access_token": access_token,
        "user": {"id": user.user_id, "email": user.email}
    })
        response.set_cookie(
            "refresh_token", refresh_token,
            httponly=True, secure=False, samesite="Lax",
            max_age=60*60*24*30, path="/auth"
        )
        return response, 200
        
@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    token = request.cookies.get("refresh_token")
    if not token:
        return jsonify({"error": "Aucun token"}), 401

    session = verify_refresh_token(token)
    if not session:
        return jsonify({"error": "Session invalide"}), 401

    new_access_token = generate_access_token(session)  # pas session.user_id

    return jsonify({"access_token": new_access_token}), 200
        
@auth_bp.route("/logout", methods=['POST'])
def logout():
    token = request.cookies.get("refresh_token")
    if not token:
        return jsonify({"error": "Aucune session active"}), 400
    with SessionLocal() as db_session:
        stmt = select(UserSession).where(UserSession.refresh_token == token)
        session = db_session.execute(stmt).scalar_one_or_none()
        if session is not None:
            db_session.delete(session)
            db_session.commit()
    response = jsonify({"message": "Déconnexion réussite"})
    response.delete_cookie("refresh_token", path="/auth")
    return response, 200
    