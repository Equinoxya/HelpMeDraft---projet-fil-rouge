"""
Écriture et lecture du journal des actions d'administration.

Les fonctions d'écriture prennent la SESSION DE BASE EN PARAMÈTRE, et ne
committent pas elles-mêmes. C'est le point important de ce module : la trace
doit être écrite dans la MÊME transaction que l'action qu'elle décrit. Si les
deux étaient séparées, deux pannes deviendraient possibles — l'action sans sa
trace, ou la trace d'une action qui n'a pas eu lieu — et un journal auquel on ne
peut pas se fier ne vaut rien.
"""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from database.db import JournalAdmin, SessionLocal, User
from utilitaires import utc_now_naive

# Les trois valeurs autorisées par la contrainte ck_journal_action de la base.
ACTIONS = ("role", "quota", "suppression")

# Rétention du journal. Ce n'est pas un réglage de confort : la table contient
# des emails, donc des données personnelles, et une conservation sans terme
# serait difficile à justifier au regard du RGPD. Un an couvre le besoin réel
# (retrouver qui a fait quoi sur l'exercice en cours) sans aller au-delà.
RETENTION_JOURS = 365


def tracer(
    db_session: Session,
    *,
    acteur: User,
    cible: User,
    action: str,
    avant: str | None = None,
    apres: str | None = None,
) -> JournalAdmin:
    """
    Ajoute une ligne au journal, SANS committer.

    L'appelant commit, en même temps que la modification tracée. Les emails sont
    copiés ici et non référencés : après une suppression, la clé étrangère ne
    désignerait plus personne, et c'est précisément l'action qu'il faut pouvoir
    relire.
    """
    if action not in ACTIONS:
        # Une action hors liste serait refusée par la base (ck_journal_action) au
        # moment du commit, c'est-à-dire trop tard pour dire laquelle était
        # fautive. On échoue ici, où le message est utile.
        raise ValueError(f"action inconnue : {action!r}. Attendu : {', '.join(ACTIONS)}")

    ligne = JournalAdmin(
        acteur_id=acteur.user_id,
        acteur_email=acteur.email,
        cible_id=cible.user_id,
        cible_email=cible.email,
        action=action,
        avant=avant,
        apres=apres,
    )
    db_session.add(ligne)
    return ligne


def purge_journal_admin(retention_jours: int = RETENTION_JOURS) -> int:
    """
    Supprime les entrées plus anciennes que la rétention, et rend leur nombre.

    Même mécanique que purge_expired_sessions : une purge opportuniste, appelée
    au fil de l'usage plutôt que par une tâche planifiée qu'il faudrait
    installer et surveiller. L'index ix_journal_date rend le balayage direct.
    """
    limite = utc_now_naive() - timedelta(days=retention_jours)
    with SessionLocal() as db_session:
        supprimees = db_session.execute(
            delete(JournalAdmin).where(JournalAdmin.created_at < limite)
        ).rowcount
        db_session.commit()
        return supprimees or 0


def lire(page: int, per_page: int, action: str | None = None) -> tuple[list[JournalAdmin], int]:
    """
    Rend une page du journal, du plus récent au plus ancien, et le total.

    Le filtre `action` est validé par l'appelant contre ACTIONS : il entre dans
    un `where` paramétré par l'ORM, jamais dans du SQL assemblé.
    """
    with SessionLocal() as db_session:
        conditions = []
        if action is not None:
            conditions.append(JournalAdmin.action == action)

        # func.count et non un select des identifiants suivi d'un len() : le
        # comptage se fait dans la base, et ne ramène pas la table entière pour
        # en mesurer la taille.
        total = db_session.execute(
            select(func.count()).select_from(JournalAdmin).where(*conditions)
        ).scalar_one()

        lignes = (
            db_session.execute(
                select(JournalAdmin)
                .where(*conditions)
                .order_by(JournalAdmin.created_at.desc(), JournalAdmin.id_action.desc())
                .limit(per_page)
                .offset((page - 1) * per_page)
            )
            .scalars()
            .all()
        )
        return list(lignes), total


def serialiser(ligne: JournalAdmin) -> dict:
    return {
        "id_action": ligne.id_action,
        "acteur_email": ligne.acteur_email,
        "cible_email": ligne.cible_email,
        "action": ligne.action,
        "avant": ligne.avant,
        "apres": ligne.apres,
        "created_at": ligne.created_at.isoformat(),
    }
