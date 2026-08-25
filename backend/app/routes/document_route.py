from flask import Blueprint, jsonify, request
from database.db import SessionLocal, Document, Dossier
from sqlalchemy import select, func
from app.routes.auth_routes import token_required

document_bp = Blueprint("documents", __name__, url_prefix="/documents")

ALLOWED_FORMATS = {"markdown", "wysiwyg"}
MAX_PER_PAGE = 50
DEFAULT_PER_PAGE = 20


@document_bp.before_request
def require_auth():
    # Un préflight CORS (OPTIONS) n'envoie jamais le header Authorization :
    # on le laisse passer sans vérifier le token, sinon Flask n'a jamais
    # l'occasion de générer sa réponse OPTIONS automatique et le navigateur
    # bloque la requête réelle qui suit (erreur "preflight ... HTTP ok status").
    # Aucune donnée n'est exposée par une réponse OPTIONS : c'est sans risque.
    if request.method == "OPTIONS":
        return None

    return token_required(lambda: None)()


def _dossier_belongs_to_user(db_session, id_dossier: str, user_id: str) -> bool:
    stmt = select(Dossier).where(
        Dossier.id_dossier == id_dossier,
        Dossier.user_id == user_id,
    )
    return db_session.execute(stmt).scalar_one_or_none() is not None


def _serialize_document(document: Document) -> dict:
    return {
        "id_document": document.id_document,
        "titre": document.titre,
        "content": document.content,
        "format": document.format,
        "id_dossier": document.id_dossier,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
    }


def _validate_document_fields(data: dict, partial: bool = False):
    """
    Valide les champs titre/content/format/id_dossier d'un payload.
    - partial=False (création) : titre requis, tous les champs retournés avec défauts.
    - partial=True (mise à jour) : seuls les champs présents dans `data` sont validés
      et retournés ; les absents ne sont pas touchés par l'appelant.

    Retourne (champs_valides: dict, erreur: None) ou (None, (réponse_json, code_http)).
    """
    fields = {}

    if not partial or "titre" in data:
        titre = data.get("titre")
        if not titre or not isinstance(titre, str) or not titre.strip():
            return None, (jsonify({"error": "Le champ titre est requis"}), 400)
        titre = titre.strip()
        if len(titre) > 255:
            return None, (jsonify({"error": "Le titre ne peut pas dépasser 255 caractères"}), 400)
        fields["titre"] = titre

    if not partial or "content" in data:
        content = data.get("content")
        if content is not None and not isinstance(content, str):
            return None, (jsonify({"error": "Le champ content doit être une chaîne de caractères"}), 400)
        fields["content"] = content

    if not partial or "format" in data:
        doc_format = data.get("format", "markdown")
        if doc_format not in ALLOWED_FORMATS:
            return None, (jsonify({"error": f"Le format doit être l'un de : {', '.join(sorted(ALLOWED_FORMATS))}"}), 400)
        fields["format"] = doc_format

    if not partial or "id_dossier" in data:
        id_dossier = data.get("id_dossier")
        if id_dossier is not None and not isinstance(id_dossier, str):
            return None, (jsonify({"error": "id_dossier doit être une chaîne de caractères"}), 400)
        fields["id_dossier"] = id_dossier

    return fields, None


@document_bp.route("", methods=["POST"])
def create_document():
    data = request.get_json(silent=True) or {}

    fields, error = _validate_document_fields(data, partial=False)
    if error is not None:
        return error

    with SessionLocal() as db_session:
        if fields["id_dossier"] is not None:
            if not _dossier_belongs_to_user(db_session, fields["id_dossier"], request.user_id):
                return jsonify({"error": "Dossier introuvable"}), 404

        new_document = Document(
            titre=fields["titre"],
            content=fields["content"],
            format=fields["format"],
            id_dossier=fields["id_dossier"],
            user_id=request.user_id,
        )
        db_session.add(new_document)
        db_session.commit()
        db_session.refresh(new_document)

        return jsonify(_serialize_document(new_document)), 201


@document_bp.route("", methods=["GET"])
def list_documents():
    id_dossier = request.args.get("id_dossier")

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
        stmt = select(Document).where(Document.user_id == request.user_id)
        count_stmt = select(func.count()).select_from(Document).where(Document.user_id == request.user_id)

        if id_dossier is not None:
            if not _dossier_belongs_to_user(db_session, id_dossier, request.user_id):
                return jsonify({"error": "Dossier introuvable"}), 404
            stmt = stmt.where(Document.id_dossier == id_dossier)
            count_stmt = count_stmt.where(Document.id_dossier == id_dossier)

        total = db_session.execute(count_stmt).scalar_one()

        stmt = stmt.order_by(Document.updated_at.desc()).limit(per_page).offset((page - 1) * per_page)
        documents = db_session.execute(stmt).scalars().all()

        return jsonify({
            "items": [_serialize_document(d) for d in documents],
            "page": page,
            "per_page": per_page,
            "total": total,
        }), 200


@document_bp.route("/<id_document>", methods=["GET"])
def get_document(id_document):
    with SessionLocal() as db_session:
        stmt = select(Document).where(
            Document.id_document == id_document,
            Document.user_id == request.user_id,
        )
        document = db_session.execute(stmt).scalar_one_or_none()
        if document is None:
            return jsonify({"error": "Document introuvable"}), 404

        return jsonify(_serialize_document(document)), 200


@document_bp.route("/<id_document>", methods=["PUT"])
def update_document(id_document):
    data = request.get_json(silent=True) or {}

    fields, error = _validate_document_fields(data, partial=True)
    if error is not None:
        return error

    with SessionLocal() as db_session:
        stmt = select(Document).where(
            Document.id_document == id_document,
            Document.user_id == request.user_id,
        )
        document = db_session.execute(stmt).scalar_one_or_none()
        if document is None:
            return jsonify({"error": "Document introuvable"}), 404

        if "id_dossier" in fields and fields["id_dossier"] is not None:
            if not _dossier_belongs_to_user(db_session, fields["id_dossier"], request.user_id):
                return jsonify({"error": "Dossier introuvable"}), 404

        for key, value in fields.items():
            setattr(document, key, value)

        db_session.commit()
        db_session.refresh(document)

        return jsonify(_serialize_document(document)), 200


@document_bp.route("/<id_document>", methods=["DELETE"])
def delete_document(id_document):
    with SessionLocal() as db_session:
        stmt = select(Document).where(
            Document.id_document == id_document,
            Document.user_id == request.user_id,
        )
        document = db_session.execute(stmt).scalar_one_or_none()
        if document is None:
            return jsonify({"error": "Document introuvable"}), 404

        db_session.delete(document)
        db_session.commit()

        return "", 204