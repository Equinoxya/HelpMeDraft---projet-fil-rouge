"""
Jeu d'essai — jeu de données de test reproductible.

OBJET : peupler une base VIDE avec un jeu de données couvrant tous les cas que
l'application doit savoir traiter, pour pouvoir dérouler une recette ou une
démonstration sans cliquer pendant un quart d'heure, et sur les MÊMES données à
chaque fois.

POURQUOI UN SCRIPT PYTHON ET PAS UN .sql — deux raisons, et la première est
rédhibitoire :

  1. Les mots de passe sont stockés en empreinte bcrypt, et bcrypt tire un sel
     AU HASARD à chaque appel. Un INSERT avec une empreinte écrite en dur dans
     un fichier .sql serait donc une empreinte figée, versionnée, et partagée
     par tous les comptes du jeu d'essai : exactement ce que le salage sert à
     empêcher. Le script appelle hash_password(), la même fonction que
     /auth/register.

  2. Le script passe par l'ORM, donc par les mêmes contraintes et les mêmes
     valeurs par défaut que l'application. Il fonctionne sans modification sur
     SQLite (développement) comme sur MySQL (conteneur), là où un .sql aurait
     dû être écrit deux fois.

CE QUE LE JEU COUVRE, et pourquoi chaque ligne existe :

  • un compte ADMINISTRATEUR, sans quoi le back-office est inatteignable ;
  • trois comptes utilisateurs, dont un AU QUOTA ÉPUISÉ et un AU QUOTA MINIMAL
    (1), les deux bornes de la règle RG-07 ;
  • un DEUXIÈME utilisateur avec ses propres documents : le cloisonnement
    (RG-01) ne peut pas se tester avec un seul compte ;
  • les TROIS statuts de document (brouillon, à relire, terminé) et les deux
    formats, c'est-à-dire toutes les valeurs admises par les contraintes CHECK ;
  • un document SANS DOSSIER (id_dossier NULL), cas que le ON DELETE SET NULL
    doit produire et que l'affichage doit savoir rendre ;
  • des appels IA DANS et HORS de la fenêtre de 24 h, pour que le quota
    glissant soit observable ;
  • un document VOLUMINEUX, proche de IA_MAX_CONTENU_LENGTH, pour voir le
    comportement de l'éditeur et l'estimation d'attente sur un cas réaliste ;
  • un jeton de réinitialisation EXPIRÉ et un valide, les deux branches de
    /auth/reset-password.

EXÉCUTION (depuis backend/) :

    python database/jeu_essai.py                 # base de développement SQLite
    python database/jeu_essai.py --vider         # purge d'abord les 7 tables
    HELPMEDRAFT_DB_URL=mysql+pymysql://helpmedraft_migration:MDP@127.0.0.1:3306/helpmedraft \
        python database/jeu_essai.py

Le compte de MIGRATION est indiqué pour MySQL, pas celui de l'application :
--vider exécute des DELETE massifs, qui n'ont pas à être permis au service qui
tourne en continu.

GARDE-FOU : le script REFUSE de s'exécuter sur une base qui contient déjà des
comptes, sauf --vider explicite. Sans ce contrôle, un lancement distrait sur la
base de recette ajouterait des doublons, ou pire sur une base réelle.

MOT DE PASSE unique pour tous les comptes, affiché en fin d'exécution. C'est un
jeu d'essai : il n'a aucune valeur de secret et ne doit jamais être chargé
ailleurs que sur une base de test.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from datetime import timedelta

# Le script est lancé depuis backend/ (« python database/jeu_essai.py »), donc
# son répertoire — database/ — est en tête du chemin d'import, et non backend/.
# Sans cette ligne, « from database.db import ... » échoue avec
# ModuleNotFoundError alors que tout est en place.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.services.auth_service import hash_password  # noqa: E402
from database.db import (  # noqa: E402
    IA,
    Consentement,
    Document,
    Dossier,
    PasswordReset,
    SessionLocal,
    User,
    UserSession,
)
from utilitaires import utc_now_naive  # noqa: E402

MDP_JEU_ESSAI = "JeuDEssai1"

# Ordre de purge : l'INVERSE des dépendances de clés étrangères. Les tables
# filles d'abord, `user` en dernier. Dans l'autre sens, le DELETE sur `user`
# serait refusé — ou, pire, emporterait tout par cascade et masquerait une
# erreur dans cette liste.
TABLES_A_VIDER = (IA, PasswordReset, UserSession, Consentement, Document, Dossier, User)

# Un contenu long, mais sous IA_MAX_CONTENU_LENGTH (3 000 par défaut) : le but
# est un document réaliste à éditer, pas un cas d'erreur — celui-là est déjà
# couvert par les tests d'intégration.
PARAGRAPHE = (
    "Le présent document constitue une note de service relative à "
    "l'organisation du travail au sein du service concerné. Il précise les "
    "modalités applicables ainsi que les délais à respecter. "
)
CONTENU_LONG = "# Note de service\n\n" + (PARAGRAPHE * 12)


def _vider(session) -> None:
    for modele in TABLES_A_VIDER:
        session.query(modele).delete()
    session.commit()


def _creer_utilisateur(session, email, prenom, nom, role="user", quota=20) -> User:
    utilisateur = User(
        email=email,
        firstname=prenom,
        lastname=nom,
        mdp_hash=hash_password(MDP_JEU_ESSAI),
        role=role,
        quota_daily_limit=quota,
    )
    session.add(utilisateur)
    # Le consentement est posé pour chaque compte : l'inscription par
    # /auth/register l'exige, un compte du jeu d'essai qui n'en aurait pas
    # serait dans un état que l'application ne sait pas produire.
    session.add(
        Consentement(
            type_consentement="traitement_ia_local",
            accepte=True,
            user=utilisateur,
        )
    )
    return utilisateur


def peupler(vider: bool) -> None:
    with SessionLocal() as session:
        comptes_existants = session.query(User).count()
        if comptes_existants and not vider:
            raise SystemExit(
                f"La base contient déjà {comptes_existants} compte(s). "
                "Le jeu d'essai ne s'ajoute pas à des données existantes : il "
                "créerait des doublons.\n"
                "Relancer avec --vider pour purger les sept tables d'abord, en "
                "s'étant assuré qu'il s'agit bien d'une base de test."
            )
        if vider:
            _vider(session)

        maintenant = utc_now_naive()

        # ── Comptes ──────────────────────────────────────────────────────────
        admin = _creer_utilisateur(session, "admin@helpmedraft.test", "Awa", "Diallo", role="admin")
        # Quota 20 (le défaut) et 15 appels déjà consommés : il reste de la
        # marge, c'est le compte sur lequel démontrer l'IA.
        camille = _creer_utilisateur(session, "camille@helpmedraft.test", "Camille", "Moreau")
        # Quota ÉPUISÉ : 20 appels dans les 24 h. Le 21e doit renvoyer 429.
        karim = _creer_utilisateur(session, "karim@helpmedraft.test", "Karim", "Benali")
        # Quota au MINIMUM autorisé par ck_user_quota. À 0, la contrainte
        # refuserait la ligne : la borne basse est 1, alignée sur MIN_QUOTA de
        # app/routes/admin_route.py (KAN-98).
        lena = _creer_utilisateur(session, "lena@helpmedraft.test", "Lena", "Petit", quota=1)
        session.commit()

        # ── Dossiers ─────────────────────────────────────────────────────────
        contrats = Dossier(name="Contrats", user=camille)
        rh = Dossier(name="Ressources humaines", user=camille)
        # Un dossier appartenant à un AUTRE compte : toute requête de Camille
        # qui le renverrait serait une fuite (RG-01).
        dossier_karim = Dossier(name="Dossier de Karim", user=karim)
        session.add_all([contrats, rh, dossier_karim])
        session.commit()

        # ── Documents : les trois statuts, les deux formats, et sans dossier ──
        documents = [
            Document(
                titre="Contrat de prestation — brouillon",
                content="# Contrat de prestation\n\nEntre les soussignés…",
                status="brouillon",
                format="markdown",
                dossier=contrats,
                user=camille,
            ),
            Document(
                titre="Avenant n°2 — à relire",
                content="## Avenant n°2\n\nLe présent avenant modifie l'article 4.",
                status="a_relire",
                format="markdown",
                dossier=contrats,
                user=camille,
            ),
            Document(
                titre="Note de service — terminée",
                content=CONTENU_LONG,
                status="termine",
                format="wysiwyg",
                dossier=rh,
                user=camille,
            ),
            # id_dossier NULL : c'est l'état que produit la suppression d'un
            # dossier (ON DELETE SET NULL). L'affichage doit le rendre sans
            # planter sur un dossier absent.
            Document(
                titre="Brouillon sans dossier",
                content="Quelques idées en vrac.",
                status="brouillon",
                user=camille,
            ),
            # Contenu vide : la colonne est nullable, et l'éditeur doit ouvrir
            # un document neuf sans contenu.
            Document(titre="Document vierge", content=None, status="brouillon", user=camille),
            Document(
                titre="Compte rendu de Karim",
                content="Réunion du 12 mars.",
                status="termine",
                dossier=dossier_karim,
                user=karim,
            ),
            Document(titre="Essai de Lena", content="Premier essai.", user=lena),
        ]
        session.add_all(documents)
        session.commit()

        contrat, avenant, note, _, _, doc_karim, doc_lena = documents

        # ── Historique IA : dans et hors de la fenêtre glissante de 24 h ──────
        appels = []
        # Camille : 15 appels récents sur un quota de 20. Il en reste 5.
        for index in range(15):
            appels.append(
                IA(
                    type_action=("reformuler", "corriger", "completer")[index % 3],
                    content_before="Texte avant.",
                    content_after="Texte après.",
                    tokens_used=40 + index,
                    user=camille,
                    document=contrat if index % 2 else avenant,
                    created_at=maintenant - timedelta(hours=index % 20),
                )
            )
        # Karim : quota épuisé, 20 appels dans la fenêtre. Le suivant est refusé.
        for index in range(20):
            appels.append(
                IA(
                    type_action="corriger",
                    content_before="Avant.",
                    content_after="Après.",
                    tokens_used=30,
                    user=karim,
                    document=doc_karim,
                    created_at=maintenant - timedelta(hours=1, minutes=index),
                )
            )
        # HORS fenêtre, à 30 h : ces appels ne doivent PAS être comptés. Sans
        # eux, une fenêtre fixe (« depuis minuit ») et une fenêtre glissante
        # donneraient le même résultat, et le test ne prouverait rien.
        for index in range(5):
            appels.append(
                IA(
                    type_action="reformuler",
                    content_before="Ancien texte.",
                    content_after="Ancien résultat.",
                    tokens_used=25,
                    user=lena,
                    document=doc_lena,
                    created_at=maintenant - timedelta(hours=30 + index),
                )
            )
        session.add_all(appels)

        # ── Jetons de réinitialisation : un valide, un expiré, un consommé ────
        session.add_all(
            [
                PasswordReset(
                    user=camille,
                    token_hash="a" * 64,
                    expires_at=maintenant + timedelta(hours=1),
                ),
                PasswordReset(
                    user=camille,
                    token_hash="b" * 64,
                    expires_at=maintenant - timedelta(hours=1),
                ),
                PasswordReset(
                    user=karim,
                    token_hash="c" * 64,
                    expires_at=maintenant + timedelta(hours=1),
                    used=True,
                ),
            ]
        )
        # Une session révoquée et une expirée : les deux cas que /auth/refresh
        # doit refuser, et que la purge KAN-96 doit ramasser. Les empreintes
        # sont fictives — aucun refresh token réel ne leur correspond, donc
        # aucune de ces sessions n'est utilisable, ce qui est voulu.
        session.add_all(
            [
                UserSession(
                    user=camille,
                    refresh_token_hash="d" * 64,
                    refresh_token_exp=maintenant + timedelta(days=7),
                ),
                UserSession(
                    user=camille,
                    refresh_token_hash="e" * 64,
                    refresh_token_exp=maintenant + timedelta(days=7),
                    revoke=True,
                ),
                UserSession(
                    user=karim,
                    refresh_token_hash="f" * 64,
                    refresh_token_exp=maintenant - timedelta(days=1),
                ),
            ]
        )
        session.commit()

        print("Jeu d'essai chargé.\n")
        print(f"  utilisateurs   {session.query(User).count()}")
        print(f"  dossiers       {session.query(Dossier).count()}")
        print(f"  documents      {session.query(Document).count()}")
        print(f"  appels IA      {session.query(IA).count()}")
        print(f"  consentements  {session.query(Consentement).count()}")
        print(f"  sessions       {session.query(UserSession).count()}")
        print(f"  réinit. mdp    {session.query(PasswordReset).count()}")
        print(f"\n  Mot de passe commun à tous les comptes : {MDP_JEU_ESSAI}")
        print("  (sans valeur de secret — base de test uniquement)\n")
        print(f"  {admin.email:34} administrateur, back-office")
        print(f"  {camille.email:34} 5 documents, 15 appels IA sur 20")
        print(f"  {karim.email:34} quota ÉPUISÉ — le prochain appel renvoie 429")
        print(f"  {lena.email:34} quota 1, et 5 appels hors fenêtre de 24 h")


if __name__ == "__main__":
    analyseur = argparse.ArgumentParser(
        description="Charge le jeu d'essai de HelpMeDraft dans la base désignée "
        "par HELPMEDRAFT_DB_URL."
    )
    analyseur.add_argument(
        "--vider",
        action="store_true",
        help="Purge les sept tables avant le chargement. Exigé si la base "
        "contient déjà des comptes.",
    )
    peupler(analyseur.parse_args().vider)
