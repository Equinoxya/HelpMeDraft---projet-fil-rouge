from flask import Blueprint, jsonify, request
from database.db import SessionLocal, Document, IA, User
from sqlalchemy import select, func
from app.routes.auth_routes import token_required
from app.services.ia_service import build_prompt, call_ollama
from utilitaires import utc_now_naive
from datetime import timedelta

ia_bp = Blueprint("ia", __name__, url_prefix="/documents")

ALLOWED_TYPE_ACTIONS = {"reformuler", "corriger", "completer"}
ALLOWED_SCOPES = {"selection", "document"}
MAX_CONTENU_LENGTH = 20000       # évite d'envoyer des payloads démesurés à Ollama
MAX_INSTRUCTIONS_LENGTH = 500


@ia_bp.before_request
def require_auth():
    if request.method == "OPTIONS":
        return None
    return token_required(lambda: None)()


def _get_owned_document(db_session, id_document: str):
    stmt = select(Document).where(
        Document.id_document == id_document,
        Document.user_id == request.user_id,
    )
    return db_session.execute(stmt).scalar_one_or_none()


@ia_bp.route("/<id_document>/ia/generer", methods=["POST"])
def generer_ia(id_document):
    data = request.get_json(silent=True) or {}

    type_action = data.get("type_action")
    scope = data.get("scope")
    contenu = data.get("contenu")
    instructions = data.get("instructions")

    if type_action not in ALLOWED_TYPE_ACTIONS:
        return jsonify({"error": f"type_action doit être l'un de : {', '.join(sorted(ALLOWED_TYPE_ACTIONS))}"}), 400

    if scope not in ALLOWED_SCOPES:
        return jsonify({"error": f"scope doit être l'un de : {', '.join(sorted(ALLOWED_SCOPES))}"}), 400

    if not contenu or not isinstance(contenu, str) or not contenu.strip():
        return jsonify({"error": "Le champ contenu est requis"}), 400

    if len(contenu) > MAX_CONTENU_LENGTH:
        return jsonify({"error": f"Le contenu ne peut pas dépasser {MAX_CONTENU_LENGTH} caractères"}), 400

    if instructions is not None:
        if not isinstance(instructions, str):
            return jsonify({"error": "Le champ instructions doit être une chaîne de caractères"}), 400
        if len(instructions) > MAX_INSTRUCTIONS_LENGTH:
            return jsonify({"error": f"Les instructions ne peuvent pas dépasser {MAX_INSTRUCTIONS_LENGTH} caractères"}), 400

    with SessionLocal() as db_session:
        document = _get_owned_document(db_session, id_document)
        if document is None:
            return jsonify({"error": "Document introuvable"}), 404
        current_user = db_session.execute(
            select(User).where(User.user_id == request.user_id)
        ).scalar_one_or_none()
        if current_user is None:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        window_start = utc_now_naive() - timedelta(hours=24)
        calls_last_24h = db_session.execute(
            select(func.count()).select_from(IA).where(
                IA.user_id == request.user_id,
                IA.created_at >= window_start,
            )
        ).scalar_one()

        if calls_last_24h >= current_user.quota_daily_limit:
            return jsonify({
                "error": f"Quota IA quotidien atteint ({current_user.quota_daily_limit} requêtes / 24h)."
            }), 429
        prompt = build_prompt(type_action, contenu, instructions)

        try:
            content_after, tokens_used = call_ollama(prompt)
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 502

        new_ia = IA(
            type_action=type_action,
            content_before=contenu,
            content_after=content_after,
            tokens_used=tokens_used,
            user_id=request.user_id,
            id_document=id_document,
        )
        db_session.add(new_ia)
        db_session.commit()
        db_session.refresh(new_ia)

        return jsonify({
            "id_ia": new_ia.id_ia,
            "content_after": content_after,
            "tokens_used": tokens_used,
        }), 201


@ia_bp.route("/<id_document>/ia/historique", methods=["GET"])
def historique_ia(id_document):
    with SessionLocal() as db_session:
        document = _get_owned_document(db_session, id_document)
        if document is None:
            return jsonify({"error": "Document introuvable"}), 404

        stmt = (
            select(IA)
            .where(IA.id_document == id_document, IA.user_id == request.user_id)
            .order_by(IA.created_at.desc())
        )
        entries = db_session.execute(stmt).scalars().all()

        return jsonify([
            {
                "id_ia": entry.id_ia,
                "type_action": entry.type_action,
                "content_before": entry.content_before,
                "content_after": entry.content_after,
                "tokens_used": entry.tokens_used,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in entries
        ]), 200