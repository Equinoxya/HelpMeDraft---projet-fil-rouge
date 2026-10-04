from datetime import timedelta

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import func, select

from app.routes.auth_routes import token_required
from app.services.ia_service import build_prompt, call_ollama, temperature_pour
from database.db import IA, Document, SessionLocal, User
from utilitaires import utc_now_naive

ia_bp = Blueprint("ia", __name__, url_prefix="/documents")

ALLOWED_TYPE_ACTIONS = {"reformuler", "corriger", "completer"}
ALLOWED_SCOPES = {"selection", "document"}
MAX_INSTRUCTIONS_LENGTH = 500


def _max_contenu() -> int:
    """
    Taille maximale du contenu soumis à l'IA, lue dans la configuration.

    La valeur dépend de la machine d'exécution : ce qu'elle peut générer avant
    le délai maximum borne ce qu'elle peut accepter en entrée, puisque
    reformuler produit à peu près autant de texte qu'il en reçoit. Voir
    IA_MAX_CONTENU_LENGTH dans app/config.py.
    """
    return current_app.config["IA_MAX_CONTENU_LENGTH"]


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
        return jsonify(
            {"error": f"type_action doit être l'un de : {', '.join(sorted(ALLOWED_TYPE_ACTIONS))}"}
        ), 400

    if scope not in ALLOWED_SCOPES:
        return jsonify(
            {"error": f"scope doit être l'un de : {', '.join(sorted(ALLOWED_SCOPES))}"}
        ), 400

    if not contenu or not isinstance(contenu, str) or not contenu.strip():
        return jsonify({"error": "Le champ contenu est requis"}), 400

    if len(contenu) > _max_contenu():
        return jsonify(
            {"error": f"Le contenu ne peut pas dépasser {_max_contenu()} caractères"}
        ), 400

    if instructions is not None:
        if not isinstance(instructions, str):
            return jsonify(
                {"error": "Le champ instructions doit être une chaîne de caractères"}
            ), 400
        if len(instructions) > MAX_INSTRUCTIONS_LENGTH:
            return jsonify(
                {
                    "error": f"Les instructions ne peuvent pas dépasser {MAX_INSTRUCTIONS_LENGTH} caractères"
                }
            ), 400

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
            select(func.count())
            .select_from(IA)
            .where(
                IA.user_id == request.user_id,
                IA.created_at >= window_start,
            )
        ).scalar_one()

        if calls_last_24h >= current_user.quota_daily_limit:
            return jsonify(
                {
                    "error": f"Quota IA quotidien atteint ({current_user.quota_daily_limit} requêtes / 24h)."
                }
            ), 429
        prompt = build_prompt(type_action, contenu, instructions)

        try:
            content_after, tokens_used = call_ollama(
                prompt, temperature=temperature_pour(type_action)
            )
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

        return jsonify(
            {
                "id_ia": new_ia.id_ia,
                "content_after": content_after,
                "tokens_used": tokens_used,
            }
        ), 201


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

        return jsonify(
            [
                {
                    "id_ia": entry.id_ia,
                    "type_action": entry.type_action,
                    "content_before": entry.content_before,
                    "content_after": entry.content_after,
                    "tokens_used": entry.tokens_used,
                    "created_at": entry.created_at.isoformat(),
                    # Traçabilité AI Act : le client a besoin de distinguer une
                    # proposition rejetée d'une proposition versée au document.
                    "insere": entry.insere,
                    "position_debut": entry.position_debut,
                    "insere_at": entry.insere_at.isoformat() if entry.insere_at else None,
                }
                for entry in entries
            ]
        ), 200


# Borne du décalage accepté. Elle suit la taille maximale d'un document, pas
# celle du texte soumis à l'IA : l'insertion peut viser n'importe quel point du
# document, y compris au-delà de ce qu'on accepte d'envoyer au modèle.
MAX_POSITION_DEBUT = 1_000_000


@ia_bp.route("/<id_document>/ia/<id_ia>/insertion", methods=["POST"])
def marquer_insertion(id_document, id_ia):
    """
    Marque une proposition comme versée au document (AI Act, art. 50).

    La ligne `ia` atteste que le modèle a PRODUIT un texte ; cette route
    atteste que l'utilisateur l'a ACCEPTÉ. Sans elle, une proposition rejetée
    et une proposition insérée sont indiscernables en base, et la trace exigée
    par le règlement ne vaut rien.

    IDEMPOTENTE : marquer deux fois la même interaction renvoie 200 sans rien
    changer. Le client appelle cette route après avoir modifié le contenu
    local ; un double clic, un rejeu de requête ou une reprise après coupure
    réseau ne doivent pas produire d'erreur ni réécrire l'horodatage d'origine,
    qui est la donnée que la trace conserve.
    """
    data = request.get_json(silent=True) or {}
    position_debut = data.get("position_debut")

    # isinstance(x, bool) exclu explicitement : en Python bool est une
    # sous-classe de int, donc True passerait pour un décalage de 1.
    if (
        not isinstance(position_debut, int)
        or isinstance(position_debut, bool)
        or not (0 <= position_debut <= MAX_POSITION_DEBUT)
    ):
        return jsonify(
            {"error": f"position_debut doit être un entier entre 0 et {MAX_POSITION_DEBUT}"}
        ), 400

    with SessionLocal() as db_session:
        # Propriété du document vérifiée d'abord : inutile de chercher
        # l'interaction si le document n'est pas à l'appelant.
        if _get_owned_document(db_session, id_document) is None:
            return jsonify({"error": "Document introuvable"}), 404

        # Les trois critères sont dans le WHERE, pas vérifiés après lecture :
        # l'interaction doit exister, appartenir à ce document ET à cet
        # utilisateur. Il est impossible d'oublier le contrôle sans supprimer
        # la ligne qui sélectionne.
        stmt = select(IA).where(
            IA.id_ia == id_ia,
            IA.id_document == id_document,
            IA.user_id == request.user_id,
        )
        entry = db_session.execute(stmt).scalar_one_or_none()
        if entry is None:
            # 404 et non 403 : répondre 403 confirmerait à un attaquant que
            # l'identifiant existe. Même raisonnement qu'au § 5.7.2 du dossier.
            return jsonify({"error": "Interaction introuvable"}), 404

        if not entry.insere:
            entry.insere = True
            entry.position_debut = position_debut
            entry.insere_at = utc_now_naive()
            db_session.commit()
            db_session.refresh(entry)

        return jsonify(
            {
                "id_ia": entry.id_ia,
                "insere": entry.insere,
                "position_debut": entry.position_debut,
                "insere_at": entry.insere_at.isoformat() if entry.insere_at else None,
            }
        ), 200
