from flask import Blueprint, jsonify, request
from database.db import SessionLocal, User, UserSession
from app.services.auth_service import hash_password, verify_password, generate_access_token, create_session, verify_refresh_token, generate_refresh_token
from sqlalchemy import select

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    requiered_fields = ["email", "mdp", "lastname", "firstname"]
    for field in requiered_fields:
        if not data.get(field):
            return jsonify({"error" : f"Le champ {field} est requis"}), 400
        
    email = data["email"]
    plain_password = data["mdp"]
    
    with SessionLocal() as db_session:
        stmt = select(User).where(User.email == email )
        existing_user = db_session.execute(stmt).scalar_one_or_none()
        if existing_user is not None: 
            return jsonify({"error" : "Cet email est déjà utilisé"}), 409
        new_user = User(
            email = email,
            mdp_hash = hash_password(plain_password),
            lastname = data["lastname"],
            firstname = data["firstname"],
            role = "user"
        )
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
        
        return jsonify({
            "message" : "Utilisateur crée avec succès",
            "user_id" : new_user.user_id,
            "email" : new_user.email,
        }), 201
        
@auth_bp.route("/login", methods= ["POST"])
def login():
    data = request.get_json()
    if not data.get("email") or not data.get("mdp"):
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
        
        return jsonify({
            "access_token" : access_token,
            "refresh_token" : refresh_token,
            "user": {
                "user_id" : user.user_id,
                "email" : user.email,
                "firstname" : user.firstname,
                "lastname" : user.lastname
            }
        }), 200
        
@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()
    if not data.get("refresh_token"):
        return jsonify({"error" : "Refresh token requis"}), 400
    
    try: 
        user_id = verify_refresh_token(data["refresh_token"])
    except ValueError as e:
        return jsonify({"error" : str(e)}), 401
    
    new_access_token = generate_access_token(user_id)
    return jsonify({"access_token" : new_access_token}), 200
        
@auth_bp.route("/logout", methods=['POST'])
def logout():
    data = request.get_json()
    if not data.get("refresh_token"):
        return jsonify({"error" : "refresh_token requis"}), 400
    refresh_token = data["refresh_token"]
    with SessionLocal() as db_session:
        stmt = select(UserSession).where(UserSession.refresh_token == refresh_token)
        session = db_session.execute(stmt).scalar_one_or_none()
        if session is not None:
            db_session.delete(session)
            db_session.commit()
    return jsonify({"message" : "Déconnexion réussite"}), 200
    