"""
Fixtures partagées de la suite de tests backend.

ORDRE D'EXÉCUTION CRITIQUE — les variables d'environnement sont posées avant
tout import de l'application, et ce n'est pas un détail de style :

  - app/config.py lève une RuntimeError au chargement du module si
    JWT_SECRET_KEY est absente (« fail fast, fail loud ») ;
  - database/db.py construit le moteur SQLAlchemy et crée les tables à
    l'import.

Importer l'application avant d'avoir posé ces variables ferait donc échouer la
collecte des tests, ou pire, écrirait dans la vraie base HelpMeDraft.db du
poste. D'où les `os.environ[...]` en tête de fichier, avant les imports.
"""

import os
import pathlib
import sys

# ── Environnement de test — AVANT tout import applicatif ─────────────────────
BACKEND_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

os.environ["HELPMEDRAFT_DB_URL"] = "sqlite://"  # base en mémoire, jamais sur disque
os.environ["JWT_SECRET_KEY"] = "cle-jwt-de-test-sans-valeur-en-production"
os.environ["SECRET_KEY"] = "cle-session-de-test-distincte-de-la-precedente"
# APP_ENV pilote l'attribut Secure du cookie de refresh : hors développement,
# le cookie est marqué Secure et ne part pas sur http://localhost. Les tests
# reproduisent donc le comportement de développement, et le cas Secure est
# vérifié à part en forçant COOKIE_SECURE (voir tests/security).
os.environ["APP_ENV"] = "development"
os.environ.setdefault("MAIL_SERVER", "localhost")
os.environ.setdefault("MAIL_DEFAULT_SENDER", "tests@helpmedraft.local")

from datetime import timedelta  # noqa: E402

import pytest  # noqa: E402

from app import create_app  # noqa: E402
from app.extension import limiter  # noqa: E402
from app.services.auth_service import hash_password  # noqa: E402
from database.db import (  # noqa: E402
    IA,
    Base,
    Document,
    Dossier,
    SessionLocal,
    User,
    UserSession,
    engine,
)
from utilitaires import utc_now_naive  # noqa: E402

MDP_VALIDE = "MotDePasse1"


# ── Isolation ────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def base_vierge():
    """
    Recrée le schéma avant chaque test.

    autouse=True : l'isolation n'est pas une option qu'un test peut oublier de
    demander. Un test qui verrait les données d'un autre passerait ou
    échouerait selon l'ordre d'exécution, ce qui est pire qu'un test absent.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


# ── Application ──────────────────────────────────────────────────────────────


@pytest.fixture
def app():
    application = create_app()
    application.config.update(
        TESTING=True,
        MAIL_SUPPRESS_SEND=True,
        RATELIMIT_ENABLED=False,
    )
    # La limitation de débit est désactivée explicitement : /auth/login est
    # plafonné à 5 appels par minute, ce qui ferait échouer en 429 tous les
    # tests d'authentification au-delà du cinquième. Le comportement de la
    # limitation est vérifié à part (test_securite), pas subi partout.
    limiter.enabled = False

    # Flask-Mail fige sa configuration dans son objet d'état au moment du
    # init_app() : renseigner MAIL_SUPPRESS_SEND dans app.config après coup
    # n'a aucun effet, et /auth/forgot-password tenterait une vraie connexion
    # SMTP. On agit donc sur l'état de l'extension, pas sur la configuration.
    #
    # L'expéditeur est fixé ici plutôt que lu dans .env : un test ne doit pas
    # dépendre de la configuration locale de la machine qui l'exécute, sinon
    # il passe chez l'un et échoue chez l'autre, ou en intégration continue où
    # aucun .env n'existe.
    application.config.update(MAIL_DEFAULT_SENDER="tests@example.test")
    etat_mail = application.extensions.get("mail")
    if etat_mail is not None:
        etat_mail.suppress = True
        etat_mail.default_sender = "tests@example.test"
    return application


@pytest.fixture
def client(app):
    return app.test_client()


# ── Jeux de données ──────────────────────────────────────────────────────────


def _creer_utilisateur(email, role="user", mdp=MDP_VALIDE, quota=20):
    with SessionLocal() as session:
        utilisateur = User(
            email=email,
            mdp_hash=hash_password(mdp),
            lastname="Dupont",
            firstname="Camille",
            role=role,
            quota_daily_limit=quota,
        )
        session.add(utilisateur)
        session.commit()
        session.refresh(utilisateur)
        return utilisateur.user_id


@pytest.fixture
def creer_utilisateur():
    """Fabrique d'utilisateurs : rend l'identifiant du compte créé."""
    return _creer_utilisateur


@pytest.fixture
def utilisateur(creer_utilisateur):
    return creer_utilisateur("camille@exemple.fr")


@pytest.fixture
def autre_utilisateur(creer_utilisateur):
    """Second compte, pour tous les tests de cloisonnement (RG-01)."""
    return creer_utilisateur("dominique@exemple.fr")


@pytest.fixture
def administrateur(creer_utilisateur):
    return creer_utilisateur("admin@exemple.fr", role="admin")


def _entetes(client, email, mdp=MDP_VALIDE):
    reponse = client.post("/auth/login", json={"email": email, "mdp": mdp})
    assert reponse.status_code == 200, f"connexion impossible : {reponse.get_json()}"
    return {"Authorization": f"Bearer {reponse.get_json()['access_token']}"}


@pytest.fixture
def entetes(client):
    """Fabrique d'en-têtes d'autorisation à partir d'une adresse mail."""
    return lambda email, mdp=MDP_VALIDE: _entetes(client, email, mdp)


@pytest.fixture
def auth(client, utilisateur):
    return _entetes(client, "camille@exemple.fr")


@pytest.fixture
def auth_autre(client, autre_utilisateur):
    return _entetes(client, "dominique@exemple.fr")


@pytest.fixture
def auth_admin(client, administrateur):
    return _entetes(client, "admin@exemple.fr")


# ── Fabriques de contenu ─────────────────────────────────────────────────────


@pytest.fixture
def creer_document():
    def _creer(
        user_id, titre="Note de service", contenu="Bonjour.", id_dossier=None, status="brouillon"
    ):
        with SessionLocal() as session:
            document = Document(
                titre=titre,
                content=contenu,
                status=status,
                id_dossier=id_dossier,
                user_id=user_id,
            )
            session.add(document)
            session.commit()
            session.refresh(document)
            return document.id_document

    return _creer


@pytest.fixture
def creer_dossier():
    def _creer(user_id, nom="Contrats"):
        with SessionLocal() as session:
            dossier = Dossier(name=nom, user_id=user_id)
            session.add(dossier)
            session.commit()
            session.refresh(dossier)
            return dossier.id_dossier

    return _creer


@pytest.fixture
def creer_appels_ia():
    """
    Insère des appels IA directement en base, avec un horodatage choisi.

    Indispensable pour tester le quota (RG-07) : passer par la route exigerait
    20 appels réels au modèle, et ne permettrait pas de placer un appel
    au-delà de la fenêtre de 24 h pour vérifier qu'elle est bien glissante.
    """

    def _creer(user_id, id_document, nombre=1, heures_avant=0):
        instant = utc_now_naive() - timedelta(hours=heures_avant)
        with SessionLocal() as session:
            for _ in range(nombre):
                session.add(
                    IA(
                        type_action="reformuler",
                        content_before="avant",
                        content_after="après",
                        tokens_used=10,
                        user_id=user_id,
                        id_document=id_document,
                        created_at=instant,
                    )
                )
            session.commit()

    return _creer


@pytest.fixture
def ollama_double(monkeypatch):
    """
    Remplace l'appel au modèle par un double.

    Le double est posé sur `app.routes.ia_route.call_ollama` et non sur
    `app.services.ia_service.call_ollama` : la route fait
    `from app.services.ia_service import call_ollama`, donc elle détient sa
    propre référence à la fonction. Remplacer l'original dans le service
    n'aurait aucun effet sur la référence déjà importée par la route.
    """

    def _poser(retour=("Texte reformulé.", 42), exception=None):
        def _faux_appel(prompt, *args, **kwargs):
            if exception is not None:
                raise exception
            return retour

        monkeypatch.setattr("app.routes.ia_route.call_ollama", _faux_appel)

    return _poser


# ── Fixtures issues de la suite initiale (branche main) ──────────────────────
# Reprises telles quelles pour que tests/test_auth_routes.py,
# tests/test_auth_service.py et tests/test_document_routes.py continuent de
# fonctionner sans modification après la fusion des deux suites.


@pytest.fixture
def ctx(app):
    """
    Contexte d'application, nécessaire aux services qui lisent la configuration.

    auth_service et ia_service importent `current_app` pour lire JWT_SECRET_KEY
    et les paramètres Ollama. Leurs fonctions doivent donc tourner dans un
    contexte d'application, y compris en test unitaire. C'est un écart
    d'architecture rendu visible ici plutôt que masqué — voir KAN-97.
    """
    with app.app_context():
        yield app


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
    return {
        "email": COMPTE["email"],
        "mdp": COMPTE["mdp"],
        "user_id": reponse.get_json()["user_id"],
    }


@pytest.fixture
def connecte(client, compte):
    """
    Connecte le compte et renvoie de quoi exercer les routes protégées :
    headers (Authorization), refresh (jeton en clair tel que le client le
    détient) et user_id.
    """
    reponse = client.post("/auth/login", json={"email": compte["email"], "mdp": compte["mdp"]})
    assert reponse.status_code == 200, reponse.get_data(as_text=True)
    cookie = client.get_cookie("refresh_token", path="/auth")
    return {
        "headers": {"Authorization": f"Bearer {reponse.get_json()['access_token']}"},
        "refresh": cookie.value if cookie else None,
        "user_id": compte["user_id"],
    }


@pytest.fixture
def sessions_en_base():
    """
    Renvoie une fonction qui lit l'état de la table user_session.

    Les tests de rotation portent sur ce que le SERVEUR a enregistré, pas sur
    ce que la réponse HTTP annonce : c'est la seule façon de vérifier qu'on
    stocke une empreinte et non le jeton lui-même.
    """

    def lire():
        with SessionLocal() as db:
            return [(s.refresh_token_hash, s.revoke) for s in db.query(UserSession).all()]

    return lire
