from datetime import timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import func, select

from app.routes.auth_routes import token_required
from app.services import journal_service
from database.db import IA, Document, SessionLocal, User
from utilitaires import utc_now_naive

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ALLOWED_ROLES = {"user", "admin"}
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 50
MIN_QUOTA = 1
MAX_QUOTA = 1000

# Borne de la recherche : un motif à rallonge sur une table qui grossit coûte
# cher pour rien.
MAX_RECHERCHE = 128

# Caractère d'échappement déclaré à `ilike`. Voir _motif_litteral.
ECHAPPEMENT = "\\"


def _motif_litteral(recherche: str) -> str:
    """
    Transforme une recherche en motif `ilike` qui cherche le TEXTE saisi.

    Sans cela, les jokers de LIKE sont interprétés : une recherche sur « % »
    ramène la table entière, et « _ » remplace n'importe quel caractère. Ce
    n'est pas une injection — l'ORM lie la valeur, rien n'est assemblé à la main
    — mais la recherche ne fait pas ce qu'elle annonce, et un motif de jokers
    sur une grande table se paie en temps de requête. Un test le vérifie
    (TI-J20).

    L'antislash est échappé EN PREMIER : dans l'autre ordre, on échapperait les
    antislashes qu'on vient d'ajouter.
    """
    return (
        recherche.replace(ECHAPPEMENT, ECHAPPEMENT * 2)
        .replace("%", ECHAPPEMENT + "%")
        .replace("_", ECHAPPEMENT + "_")
    )


def _acteur(db_session) -> User:
    """L'administrateur qui exécute la requête, relu en base et non pris du JWT."""
    return db_session.execute(select(User).where(User.user_id == request.user_id)).scalar_one()


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
            return None, (
                jsonify(
                    {"error": f"Le rôle doit être l'un de : {', '.join(sorted(ALLOWED_ROLES))}"}
                ),
                400,
            )
        fields["role"] = role

    if "quota_daily_limit" in data:
        quota = data.get("quota_daily_limit")
        # isinstance(quota, bool) exclu explicitement : en Python, bool est une
        # sous-classe de int, donc `True`/`False` passeraient sinon la validation.
        if (
            not isinstance(quota, int)
            or isinstance(quota, bool)
            or not (MIN_QUOTA <= quota <= MAX_QUOTA)
        ):
            return None, (
                jsonify(
                    {
                        "error": f"quota_daily_limit doit être un entier entre {MIN_QUOTA} et {MAX_QUOTA}"
                    }
                ),
                400,
            )
        fields["quota_daily_limit"] = quota

    if not fields:
        return None, (
            jsonify({"error": "Aucun champ valide à mettre à jour (role, quota_daily_limit)"}),
            400,
        )

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

    recherche = (request.args.get("recherche") or "").strip()
    if len(recherche) > MAX_RECHERCHE:
        return jsonify({"error": f"recherche ne doit pas dépasser {MAX_RECHERCHE} caractères"}), 400

    with SessionLocal() as db_session:
        # Le filtre porte sur les trois champs d'identification. `ilike` avec un
        # paramètre lié par l'ORM : aucune chaîne n'est assemblée à la main, donc
        # aucune injection possible par le contenu de la recherche.
        conditions = []
        if recherche:
            motif = f"%{_motif_litteral(recherche)}%"
            conditions.append(
                User.email.ilike(motif, escape=ECHAPPEMENT)
                | User.firstname.ilike(motif, escape=ECHAPPEMENT)
                | User.lastname.ilike(motif, escape=ECHAPPEMENT)
            )

        # Le total doit compter les comptes FILTRÉS, pas tous les comptes : sinon
        # la pagination annoncerait des pages vides au-delà des résultats.
        total = db_session.execute(
            select(func.count()).select_from(User).where(*conditions)
        ).scalar_one()

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
            .where(*conditions)
            .order_by(User.created_at.asc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        rows = db_session.execute(stmt).all()

        return jsonify(
            {
                "items": [
                    _serialize_admin_user(user, nb_docs, nb_ia) for user, nb_docs, nb_ia in rows
                ],
                "page": page,
                "per_page": per_page,
                "total": total,
                "recherche": recherche,
            }
        ), 200


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
        return jsonify(
            {"error": "Vous ne pouvez pas retirer vos propres droits administrateur"}
        ), 400

    with SessionLocal() as db_session:
        stmt = select(User).where(User.user_id == user_id)
        user = db_session.execute(stmt).scalar_one_or_none()
        if user is None:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        acteur = _acteur(db_session)

        # La trace est écrite AVANT le commit, dans la même transaction que la
        # modification : les deux arrivent ensemble ou pas du tout. Séparées,
        # elles rendraient possibles une action sans trace et une trace sans
        # action — et un journal auquel on ne peut pas se fier ne sert à rien.
        #
        # Les valeurs d'avant sont lues sur l'objet AVANT de l'écraser, et seuls
        # les champs qui changent réellement sont tracés : réécrire la même
        # valeur n'est pas une action d'administration.
        for key, value in fields.items():
            ancienne = getattr(user, key)
            if ancienne == value:
                continue
            journal_service.tracer(
                db_session,
                acteur=acteur,
                cible=user,
                action="role" if key == "role" else "quota",
                avant=str(ancienne),
                apres=str(value),
            )

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

    # La confirmation est l'email du compte visé, et elle est vérifiée ICI, en
    # base. Côté interface, elle oblige à recopier l'email avant d'activer le
    # bouton ; mais une garde qui ne vit que dans le navigateur ne protège pas
    # d'un appel direct à l'API, où une erreur d'identifiant détruit le mauvais
    # compte en silence — avec toutes ses données en cascade.
    confirmation = (request.args.get("confirmation") or "").strip()
    if not confirmation:
        return jsonify(
            {
                "error": "La suppression exige le paramètre « confirmation », "
                "qui doit valoir l'email du compte à supprimer."
            }
        ), 400

    with SessionLocal() as db_session:
        stmt = select(User).where(User.user_id == user_id)
        user = db_session.execute(stmt).scalar_one_or_none()
        if user is None:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        # Comparaison sans distinction de casse : les adresses ne la
        # distinguent pas en pratique, et exiger la casse exacte ferait échouer
        # une confirmation pourtant juste.
        if confirmation.casefold() != user.email.casefold():
            return jsonify(
                {
                    "error": "La confirmation ne correspond pas à l'email du compte visé. "
                    "Aucune suppression n'a été faite."
                }
            ), 400

        acteur = _acteur(db_session)

        # Trace écrite avant la suppression, pour que les emails soient encore
        # lisibles ; elle survit à la disparition du compte parce que le journal
        # en garde une copie et n'a pas de clé étrangère vers la cible.
        journal_service.tracer(
            db_session,
            acteur=acteur,
            cible=user,
            action="suppression",
            avant=user.role,
        )

        db_session.delete(user)
        db_session.commit()

        return "", 204


@admin_bp.route("/stats", methods=["GET"])
def global_stats():
    with SessionLocal() as db_session:
        total_users = db_session.execute(select(func.count()).select_from(User)).scalar_one()
        total_documents = db_session.execute(
            select(func.count()).select_from(Document)
        ).scalar_one()

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

        return jsonify(
            {
                "total_users": total_users,
                "total_documents": total_documents,
                "total_ia_calls_today": total_ia_calls_today,
                "total_ia_calls_7j": total_ia_calls_7j,
                "documents_by_status": documents_by_status,
            }
        ), 200


@admin_bp.route("/journal", methods=["GET"])
def read_journal():
    """
    Journal des actions d'administration, du plus récent au plus ancien.

    Lecture seule, et volontairement : aucune route ne permet d'y écrire
    directement ni d'en supprimer une ligne. Un journal que l'administrateur
    peut retoucher ne prouve rien. Les seules écritures viennent des routes
    ci-dessus, dans la transaction de l'action qu'elles tracent, et la seule
    suppression vient de la purge de rétention.
    """
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", DEFAULT_PER_PAGE))
    except ValueError:
        return jsonify({"error": "page et per_page doivent être des entiers"}), 400

    if page < 1:
        return jsonify({"error": "page doit être supérieur ou égal à 1"}), 400
    if per_page < 1 or per_page > MAX_PER_PAGE:
        return jsonify({"error": f"per_page doit être compris entre 1 et {MAX_PER_PAGE}"}), 400

    action = request.args.get("action")
    if action is not None and action not in journal_service.ACTIONS:
        return jsonify(
            {"error": f"action doit être l'une de : {', '.join(journal_service.ACTIONS)}"}
        ), 400

    # Purge opportuniste de la rétention, au même endroit que la lecture : c'est
    # le moment où la table est de toute façon ouverte, et cela évite une tâche
    # planifiée à installer et à surveiller. Même choix que pour les sessions
    # expirées (purge_expired_sessions, appelée à la connexion).
    journal_service.purge_journal_admin()

    lignes, total = journal_service.lire(page, per_page, action)

    return jsonify(
        {
            "items": [journal_service.serialiser(ligne) for ligne in lignes],
            "page": page,
            "per_page": per_page,
            "total": total,
            "action": action,
            "retention_jours": journal_service.RETENTION_JOURS,
        }
    ), 200
