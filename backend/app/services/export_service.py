"""
Export des données personnelles d'un compte — RGPD art. 15 et 20.

Produit une archive ZIP en mémoire :

    helpmedraft-export-AAAAMMJJ.zip
    ├── LISEZ-MOI.txt        ce que l'archive contient, et ce qu'elle ne contient pas
    ├── donnees.json         tout, structuré et lisible par machine (art. 20)
    └── documents/
        ├── 01-ma-lettre.md  un fichier par document, lisible par un humain
        └── 02-note.md

CE QUI N'EST PAS EXPORTÉ, et pourquoi — c'est le cœur de ce module :

  • mdp_hash : une empreinte de mot de passe dans un fichier qui circule par
    courriel ou clé USB est un cadeau à qui le trouve, et elle n'a aucune
    utilité pour l'utilisateur ;
  • refresh_token_hash : matériel d'authentification. Les sessions sortent en
    métadonnées seules — dates et révocation ;
  • la table password_reset : des empreintes de jetons et des dates. Aucune
    valeur pour l'utilisateur, et c'est de la sécurité ;
  • l'email de l'ADMINISTRATEUR dans le journal d'administration : c'est la
    donnée d'un TIERS. L'utilisateur a droit à ses données, pas à l'identité de
    l'agent qui a agi sur son compte. Exporter naïvement « toutes les lignes qui
    me concernent » divulguerait cet email.

Un test cherche ces noms de colonnes dans l'archive produite : l'exclusion est
vérifiée, pas seulement intentionnelle.
"""

from __future__ import annotations

import io
import json
import re
import unicodedata
import zipfile
from datetime import datetime

from sqlalchemy import select

from database.db import (
    IA,
    Consentement,
    Document,
    Dossier,
    JournalAdmin,
    SessionLocal,
    User,
    UserSession,
)
from utilitaires import utc_now_naive

# Les noms de fichiers viennent du TITRE des documents, que l'utilisateur écrit.
# Voir nom_de_fichier_sur() : c'est la seule surface d'attaque de cet export.
LONGUEUR_MAX_NOM = 60

# Noms réservés sous Windows : un fichier ainsi nommé y est inouvrable, quelle
# que soit son extension.
RESERVES_WINDOWS = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{n}" for n in range(1, 10)),
    *(f"lpt{n}" for n in range(1, 10)),
}


def nom_de_fichier_sur(titre: str, rang: int) -> str:
    """
    Transforme un titre de document en nom de fichier sans danger.

    POURQUOI CETTE FONCTION EXISTE : le titre est écrit par l'utilisateur, et il
    devient un nom d'entrée dans une archive. Un titre valant « ../../.bashrc »
    produirait une entrée qui, extraite par un outil naïf, écrit HORS du dossier
    de destination — c'est la faille dite « zip slip ». Le nom est donc
    reconstruit à partir des seuls caractères sûrs, jamais nettoyé par
    soustraction : on garde ce qu'on autorise, au lieu de retirer ce qu'on
    redoute et d'oublier un cas.

    Le rang en préfixe règle deux problèmes d'un coup : deux documents de même
    titre ne s'écrasent pas, et un titre entièrement composé de caractères
    refusés donne quand même un nom utilisable.
    """
    # Les accents sont transposés plutôt que supprimés : « Résumé » doit donner
    # « resume » et non « rsum ».
    sans_accent = unicodedata.normalize("NFKD", titre or "")
    sans_accent = sans_accent.encode("ascii", "ignore").decode("ascii")

    # Liste blanche : lettres, chiffres, tiret, souligné. Tout le reste — dont
    # « / », « \ », « .. », les caractères de contrôle et les deux-points —
    # devient un tiret.
    base = re.sub(r"[^A-Za-z0-9]+", "-", sans_accent).strip("-").lower()
    base = base[:LONGUEUR_MAX_NOM].strip("-")

    if not base or base in RESERVES_WINDOWS:
        base = "document"

    return f"{rang:02d}-{base}.md"


def _iso(valeur: datetime | None) -> str | None:
    return valeur.isoformat() if valeur is not None else None


def collecter(user_id: str) -> dict:
    """
    Rassemble les données du compte en une structure sérialisable.

    Aucun identifiant n'est pris en paramètre depuis l'extérieur de la requête :
    l'appelant passe celui du jeton, et rien d'autre n'est accessible.
    """
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()
        if user is None:
            return {}

        dossiers = {
            dossier.id_dossier: dossier
            for dossier in session.execute(
                select(Dossier).where(Dossier.user_id == user_id).order_by(Dossier.created_at)
            ).scalars()
        }
        documents = list(
            session.execute(
                select(Document).where(Document.user_id == user_id).order_by(Document.created_at)
            ).scalars()
        )
        titres_documents = {doc.id_document: doc.titre for doc in documents}

        appels_ia = list(
            session.execute(
                select(IA).where(IA.user_id == user_id).order_by(IA.created_at)
            ).scalars()
        )
        consentements = list(
            session.execute(
                select(Consentement)
                .where(Consentement.user_id == user_id)
                .order_by(Consentement.date_consentement)
            ).scalars()
        )
        # Les sessions sortent en MÉTADONNÉES : ni l'empreinte du jeton, ni rien
        # qui permette de rejouer une connexion.
        sessions_utilisateur = list(
            session.execute(
                select(UserSession)
                .where(UserSession.user_id == user_id)
                .order_by(UserSession.created_at)
            ).scalars()
        )

        # Journal d'administration : les actions dont CE compte a été la cible,
        # SANS l'email de l'administrateur qui les a faites — donnée d'un tiers.
        actions = list(
            session.execute(
                select(JournalAdmin)
                .where(JournalAdmin.cible_id == user_id)
                .order_by(JournalAdmin.created_at)
            ).scalars()
        )

        return {
            "export": {
                "genere_le": _iso(utc_now_naive()),
                "application": "HelpMeDraft",
                "fondement": "RGPD art. 15 (droit d'accès) et art. 20 (portabilité)",
                "exclusions": (
                    "Cette archive ne contient aucun mot de passe, aucune empreinte de "
                    "mot de passe, aucun jeton de connexion, et aucune donnée "
                    "concernant une autre personne."
                ),
            },
            "compte": {
                "email": user.email,
                "prenom": user.firstname,
                "nom": user.lastname,
                "role": user.role,
                "quota_ia_quotidien": user.quota_daily_limit,
                "cree_le": _iso(user.created_at),
                "modifie_le": _iso(user.updated_at),
            },
            "consentements": [
                {
                    "type": c.type_consentement,
                    "accepte": c.accepte,
                    "date": _iso(c.date_consentement),
                }
                for c in consentements
            ],
            "dossiers": [{"nom": d.name, "cree_le": _iso(d.created_at)} for d in dossiers.values()],
            "documents": [
                {
                    "titre": doc.titre,
                    "contenu": doc.content,
                    "format": doc.format,
                    "statut": doc.status,
                    "dossier": dossiers[doc.id_dossier].name
                    if doc.id_dossier in dossiers
                    else None,
                    "cree_le": _iso(doc.created_at),
                    "modifie_le": _iso(doc.updated_at),
                }
                for doc in documents
            ],
            "historique_ia": [
                {
                    "action": appel.type_action,
                    "document": titres_documents.get(appel.id_document),
                    "texte_soumis": appel.content_before,
                    "proposition": appel.content_after,
                    "jetons_consommes": appel.tokens_used,
                    "insere_dans_le_document": appel.insere,
                    "insere_le": _iso(appel.insere_at),
                    "date": _iso(appel.created_at),
                }
                for appel in appels_ia
            ],
            "sessions": [
                {
                    "ouverte_le": _iso(s.created_at),
                    "expire_le": _iso(s.refresh_token_exp),
                    "revoquee": s.revoke,
                }
                for s in sessions_utilisateur
            ],
            "actions_administratives": [
                {
                    "action": a.action,
                    "avant": a.avant,
                    "apres": a.apres,
                    "date": _iso(a.created_at),
                }
                for a in actions
            ],
        }


LISEZ_MOI = """HelpMeDraft — export de vos données personnelles
================================================

Généré le {date}.

Cette archive répond aux articles 15 (droit d'accès) et 20 (droit à la
portabilité) du RGPD.

CE QU'ELLE CONTIENT
    donnees.json    l'ensemble de vos données, dans un format lisible par
                    machine : compte, consentements, dossiers, documents et
                    leur contenu, historique de l'assistant, métadonnées de
                    vos sessions, actions d'administration sur votre compte.
    documents/      un fichier Markdown par document, pour une relecture
                    directe. Ce sont les mêmes contenus que dans donnees.json.

CE QU'ELLE NE CONTIENT PAS, ET POURQUOI
    Aucun mot de passe, ni l'empreinte du vôtre : elle n'a aucune utilité pour
    vous, et un tel fichier circule par courriel ou clé USB.

    Aucun jeton de connexion. Vos sessions apparaissent sous forme de dates et
    d'un indicateur de révocation, jamais de la valeur qui permettrait de
    rejouer une connexion.

    Aucune donnée concernant une autre personne. Les actions d'administration
    sur votre compte sont listées, mais sans l'identité de l'administrateur qui
    les a faites : c'est sa donnée personnelle, pas la vôtre.

QUESTIONS
    rgpd@helpmedraft.fr
"""


def construire_archive(donnees: dict) -> bytes:
    """
    Assemble l'archive ZIP en mémoire.

    En mémoire et non sur disque : un fichier temporaire contenant les données
    personnelles d'un compte survivrait à une erreur, et il faudrait penser à le
    retirer. La limitation de débit de la route (5 par heure) borne le coût de ce
    choix.
    """
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "LISEZ-MOI.txt",
            LISEZ_MOI.format(date=donnees["export"]["genere_le"]),
        )
        archive.writestr(
            "donnees.json",
            json.dumps(donnees, ensure_ascii=False, indent=2),
        )
        for rang, document in enumerate(donnees["documents"], start=1):
            nom = nom_de_fichier_sur(document["titre"], rang)
            corps = f"# {document['titre']}\n\n{document['contenu'] or ''}\n"
            archive.writestr(f"documents/{nom}", corps)

    return tampon.getvalue()


def nom_archive(maintenant: datetime | None = None) -> str:
    """
    Nom du fichier proposé au téléchargement.

    Construit sur la DATE et non sur l'email : un email placé dans un en-tête
    « Content-Disposition » ouvre la porte à l'injection d'en-tête, et n'apporte
    rien — l'utilisateur sait de quel compte vient son propre export.
    """
    date = (maintenant or utc_now_naive()).strftime("%Y%m%d")
    return f"helpmedraft-export-{date}.zip"
