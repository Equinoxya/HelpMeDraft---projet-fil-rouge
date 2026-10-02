# -*- coding: utf-8 -*-
"""
Fixtures communes aux tests automatisés (§ 9.2 du dossier).

Trois contraintes du projet imposent l'ordre de ce fichier, et c'est pour cela
qu'il commence par du code avant les imports :

1. `app/config.py` LÈVE une RuntimeError si JWT_SECRET_KEY est absente
   (§ 6.3, « fail fast, fail loud »). La variable doit donc être posée AVANT
   que `app` soit importé, sinon la collecte pytest échoue au chargement.
   C'est la contrepartie assumée du refus de valeur de repli : le garde-fou
   s'applique aussi aux tests.

2. `database/db.py` crée son moteur à l'import, sur un chemin RELATIF
   (`DB_PATH = Path("HelpMeDraft.db")`). Le répertoire courant détermine donc
   où vit la base. On bascule dans un répertoire temporaire avant l'import :
   les tests travaillent sur une base jetable et ne touchent jamais à la base
   de développement.

3. `utilitaires` et `app` s'importent depuis `backend/`, pas depuis `tests/`.
   On ajoute donc `backend/` au chemin d'import.
"""
import os
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

# (1) Secret de test : jamais celui de développement, jamais celui de production.
os.environ.setdefault("JWT_SECRET_KEY", "cle-de-test-sans-valeur-en-dehors-des-tests")
os.environ.setdefault("APP_ENV", "development")

# (2) Base jetable : on se place dans un répertoire temporaire avant l'import
#     de database.db, qui résout son chemin SQLite relativement au cwd.
_TMPDIR = tempfile.mkdtemp(prefix="helpmedraft-tests-")
os.chdir(_TMPDIR)

import pytest  # noqa: E402
from app import create_app  # noqa: E402
from database.db import Base, engine, SessionLocal, UserSession  # noqa: E402


# ── Application et client ────────────────────────────────────────────────────
@pytest.fixture
def app():
    """Application de test : base recréée pour chaque cas, limiteur désactivé.

    La base est créée puis supprimée autour de CHAQUE test : un test qui échoue
    ne contamine pas le suivant, et l'ordre d'exécution n'a aucune incidence.
    Des tests qui ne passent que dans un certain ordre ne prouvent rien.

    Le limiteur de débit est neutralisé : laissé actif, il ferait échouer par
    429 toute série de tests qui se connecte plusieurs fois (§ 9.2). Il est
    vérifié séparément par un test qui le réactive explicitement (TS-05).
    """
    application = create_app()
    application.config.update(TESTING=True, RATELIMIT_ENABLED=False)

    # Aucun courriel ne part pendant les tests. /auth/forgot-password appelle
    # réellement le SMTP : sans cette ligne, le test de cette route dépend de
    # Mailtrap, donc du réseau — il échoue hors ligne et devient lent en ligne.
    # Même raisonnement que pour le double de call_ollama (§ 9.2) : un test ne
    # dépend pas d'un service externe.
    # La suppression est posée sur l'état de Flask-Mail, et pas seulement en
    # configuration : l'extension lit l'option au moment du init_app, qui a
    # déjà eu lieu dans create_app().
    # L'expéditeur est fixé ici plutôt que lu dans .env : un test ne doit pas
    # dépendre de la configuration locale de la machine qui l'exécute, sinon il
    # passe chez l'un et échoue chez l'autre (ou en intégration continue, où
    # aucun .env n'existe).
    application.config.update(MAIL_SUPPRESS_SEND=True,
                              MAIL_DEFAULT_SENDER="tests@example.test")
    etat_mail = application.extensions.get("mail")
    if etat_mail is not None:
        etat_mail.suppress = True
        etat_mail.default_sender = "tests@example.test"

    Base.metadata.create_all(engine)
    yield application
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def ctx(app):
    """Contexte d'application, nécessaire aux services qui lisent la config.

    auth_service et ia_service importent `current_app` pour lire JWT_SECRET_KEY
    et les paramètres Ollama (§ 7.2.4). Leurs fonctions doivent donc tourner
    dans un contexte d'application, y compris en test unitaire. C'est l'écart
    n° 4 du § 8.11, rendu visible ici plutôt que masqué.
    """
    Base.metadata.create_all(engine)
    with app.app_context():
        yield app
    Base.metadata.drop_all(engine)


# ── Jeu de données minimal ───────────────────────────────────────────────────
COMPTE = {
    "lastname": "Test",
    "firstname": "Utilisatrice",
    "email": "test@example.test",
    "mdp": "MotDePasse1",
    "rgpd_consent": True,
}


@pytest.fixture
def compte(client):
    """Crée un compte et renvoie ses identifiants de connexion."""
    reponse = client.post("/auth/register", json=COMPTE)
    assert reponse.status_code == 201, reponse.get_data(as_text=True)
    return {"email": COMPTE["email"], "mdp": COMPTE["mdp"],
            "user_id": reponse.get_json()["user_id"]}


@pytest.fixture
def connecte(client, compte):
    """Connecte le compte et renvoie de quoi exercer les routes protégées.

    Renvoie un dict : headers (Authorization), refresh (jeton en clair tel que
    le client le détient) et user_id.
    """
    reponse = client.post("/auth/login",
                          json={"email": compte["email"], "mdp": compte["mdp"]})
    assert reponse.status_code == 200, reponse.get_data(as_text=True)
    cookie = client.get_cookie("refresh_token", path="/auth")
    return {
        "headers": {"Authorization": f"Bearer {reponse.get_json()['access_token']}"},
        "refresh": cookie.value if cookie else None,
        "user_id": compte["user_id"],
    }


@pytest.fixture
def sessions_en_base():
    """Renvoie une fonction qui lit l'état de la table user_session.

    Les tests de rotation portent sur ce que le SERVEUR a enregistré, pas sur
    ce que la réponse HTTP annonce : c'est la seule façon de vérifier qu'on
    stocke une empreinte et non le jeton.
    """
    def lire():
        with SessionLocal() as db:
            return [(s.refresh_token_hash, s.revoke)
                    for s in db.query(UserSession).all()]
    return lire
