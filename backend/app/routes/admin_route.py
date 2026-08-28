from datetime import timedelta
from flask import Blueprint, jsonify, request
from database.db import SessionLocal, User, Document, IA
from sqlalchemy import select, func
from app.routes.auth_routes import token_required
from utilitaires import utc_now_naive

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ALLOWED_ROLES = {"user", "admin"}
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 50
MIN_QUOTA = 1
MAX_QUOTA = 1000


@admin_bp.before_request
def require_admin():
    if request.method == "OPTIONS":
        return None

    # Réutilise le décorateur d'auth existant, puis ajoute la vérification
    # de rôle par-dessus (même schéma que require_auth sur les autres blueprints).
    auth_error = token_required(lambda: None)()
    if auth_error is not None:
        return auth_error

    with SessionLocal() as db_session:
        stmt = select(User).where(User.user_id == request.user_id)
        current_user = db_session.execute(stmt).scalar_one_or_none()
        if current_user is None or current_user.role != "admin":
            return jsonify({"error": "Accès réservé aux administrateurs"}), 403


def _serialize_admin_user(user: User, nb_documents: int, nb_appels_ia: int) -> dict:
    return {
        "id": user.user_id,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "role": user.role,
        "quota_daily_limit": user.quota_daily_limit,
        "created_at": user.created_at.isoformat(),
        "nb_documents": nb_documents,
        "nb_appels_ia": nb_appels_ia,
    }


def _validate_update_payload(data: dict):
    fields = {}

    if "role" in data:
        role = data.get("role")
        if role not in ALLOWED_ROLES:
            return None, (jsonify({"error": f"Le rôle doit être l'un de : {', '.join(sorted(ALLOWED_ROLES))}"}), 400)
        fields["role"] = role

    if "quota_daily_limit" in data:
        quota = data.get("quota_daily_limit")
        # isinstance(quota, bool) exclu explicitement : en Python, bool est une
        # sous-classe de int, donc `True`/`False` passeraient sinon la validation.
        if not isinstance(quota, int) or isinstance(quota, bool) or not (MIN_QUOTA <= quota <= MAX_QUOTA):
            return None, (jsonify({"error": f"quota_daily_limit doit être un entier entre {MIN_QUOTA} et {MAX_QUOTA}"}), 400)
        fields["quota_daily_limit"] = quota

    if not fields:
        return None, (jsonify({"error": "Aucun champ valide à mettre à jour (role, quota_daily_limit)"}), 400)

    return fields, None


@admin_bp.route("/users", methods=["GET"])
def list_users():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", DEFAULT_PER_PAGE))
    except ValueError:
        return jsonify({"error": "page et per_page doivent être des entiers"}), 400

    if page < 1:
        return jsonify({"error": "page doit être supérieur ou égal à 1"}), 400
    if per_page < 1 or per_page > MAX_PER_PAGE:
        return jsonify({"error": f"per_page doit être compris entre 1 et {MAX_PER_PAGE}"}), 400

    with SessionLocal() as db_session:
        total = db_session.execute(select(func.count()).select_from(User)).scalar_one()

        # Sous-requêtes corrélées : évite un GROUP BY fragile sur toutes les
        # colonnes de User, et reste lisible avec deux compteurs distincts.
        nb_documents_subq = (
            select(func.count(Document.id_document))
            .where(Document.user_id == User.user_id)
            .correlate(User)
            .scalar_subquery()
        )
        nb_ia_subq = (
            select(func.count(IA.id_ia))
            .where(IA.user_id == User.user_id)
            .correlate(User)
            .scalar_subquery()
        )

        stmt = (
            select(User, nb_documents_subq, nb_ia_subq)
            .order_by(User.created_at.asc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        rows = db_session.execute(stmt).all()

        return jsonify({
            "items": [_serialize_admin_user(user, nb_docs, nb_ia) for user, nb_docs, nb_ia in rows],
            "page": page,
            "per_page": per_page,
            "total": total,
        }), 200


@admin_bp.route("/users/<user_id>", methods=["PATCH"])
def update_user(user_id):
    data = request.get_json(silent=True) or {}

    fields, error = _validate_update_payload(data)
    if error is not None:
        return error

    # Garde-fou : un admin ne doit pas pouvoir se retirer ses propres droits
    # par erreur (ou via un appel API direct), ce qui pourrait bloquer l'accès
    # au back-office si c'est le seul admin.
    if "role" in fields and fields["role"] != "admin" and user_id == request.user_id:
        return jsonify({"error": "Vous ne pouvez pas retirer vos propres droits administrateur"}), 400

    with SessionLocal() as db_session:
        stmt = select(User).where(User.user_id == user_id)
        user = db_session.execute(stmt).scalar_one_or_none()
        if user is None:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        for key, value in fields.items():
            setattr(user, key, value)

        db_session.commit()
        db_session.refresh(user)

        nb_documents = db_session.execute(
            select(func.count()).select_from(Document).where(Document.user_id == user.user_id)
        ).scalar_one()
        nb_appels_ia = db_session.execute(
            select(func.count()).select_from(IA).where(IA.user_id == user.user_id)
        ).scalar_one()

        return jsonify(_serialize_admin_user(user, nb_documents, nb_appels_ia)), 200


@admin_bp.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    # Idem : un admin ne peut pas se supprimer lui-même depuis le back-office.
    if user_id == request.user_id:
        return jsonify({"error": "Vous ne pouvez pas supprimer votre propre compte"}), 400

    with SessionLocal() as db_session:
        stmt = select(User).where(User.user_id == user_id)
        user = db_session.execute(stmt).scalar_one_or_none()
        if user is None:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        db_session.delete(user)
        db_session.commit()

        return "", 204


@admin_bp.route("/stats", methods=["GET"])
def global_stats():
    with SessionLocal() as db_session:
        total_users = db_session.execute(select(func.count()).select_from(User)).scalar_one()
        total_documents = db_session.execute(select(func.count()).select_from(Document)).scalar_one()

        now = utc_now_naive()
        total_ia_calls_today = db_session.execute(
            select(func.count()).select_from(IA).where(IA.created_at >= now - timedelta(hours=24))
        ).scalar_one()
        total_ia_calls_7j = db_session.execute(
            select(func.count()).select_from(IA).where(IA.created_at >= now - timedelta(days=7))
        ).scalar_one()

        status_rows = db_session.execute(
            select(Document.status, func.count()).group_by(Document.status)
        ).all()
        documents_by_status = {"brouillon": 0, "a_relire": 0, "termine": 0}
        for status, count in status_rows:
            documents_by_status[status] = count

        return jsonify({
            "total_users": total_users,
            "total_documents": total_documents,
            "total_ia_calls_today": total_ia_calls_today,
            "total_ia_calls_7j": total_ia_calls_7j,
            "documents_by_status": documents_by_status,
        }), 200