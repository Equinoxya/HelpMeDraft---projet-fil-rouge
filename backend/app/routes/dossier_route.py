from flask import Blueprint, jsonify, request
from database.db import SessionLocal, Document, Dossier
from sqlalchemy import select, func
from app.routes.auth_routes import token_required

dossier_bp = Blueprint("dossiers", __name__, url_prefix="/dossiers")


@dossier_bp.before_request
def require_auth():
    if request.method == "OPTIONS":
        return None
    return token_required(lambda: None)()


def _serialize_dossier(dossier: Dossier, document_count: int) -> dict:
    return {
        "id_dossier": dossier.id_dossier,
        "name": dossier.name,
        "created_at": dossier.created_at.isoformat(),
        "document_count": document_count,
    }


def _validate_name(data: dict):
    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        return None, (jsonify({"error": "Le nom du dossier est requis"}), 400)
    name = name.strip()
    if len(name) > 100:
        return None, (jsonify({"error": "Le nom ne peut pas dépasser 100 caractères"}), 400)
    return name, None


@dossier_bp.route("", methods=["GET"])
def list_dossiers():
    with SessionLocal() as db_session:
        stmt = (
            select(Dossier, func.count(Document.id_document))
            .outerjoin(Document, Document.id_dossier == Dossier.id_dossier)
            .where(Dossier.user_id == request.user_id)
            .group_by(Dossier.id_dossier)
            .order_by(Dossier.created_at.asc())
        )
        rows = db_session.execute(stmt).all()
        return jsonify([_serialize_dossier(dossier, count) for dossier, count in rows]), 200


@dossier_bp.route("", methods=["POST"])
def create_dossier():
    data = request.get_json(silent=True) or {}

    name, error = _validate_name(data)
    if error is not None:
        return error

    with SessionLocal() as db_session:
        new_dossier = Dossier(name=name, user_id=request.user_id)
        db_session.add(new_dossier)
        db_session.commit()
        db_session.refresh(new_dossier)

        return jsonify(_serialize_dossier(new_dossier, 0)), 201


@dossier_bp.route("/<id_dossier>", methods=["DELETE"])
def delete_dossier(id_dossier):
    with SessionLocal() as db_session:
        stmt = select(Dossier).where(
            Dossier.id_dossier == id_dossier,
            Dossier.user_id == request.user_id,
        )
        dossier = db_session.execute(stmt).scalar_one_or_none()
        if dossier is None:
            return jsonify({"error": "Dossier introuvable"}), 404

        db_session.delete(dossier)
        db_session.commit()

        return "", 204