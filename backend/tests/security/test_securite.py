"""
Tests de non-régression des parades de sécurité — TSEC-06 à TSEC-13.

Reprise du script `backend/test_securite.py`, qui imprimait des traces sans
assertion : le contenu était pertinent, c'est le harnais qui manquait.

Les tests XSS (TSEC-01 à TSEC-05) sont côté frontend, là où l'assainissement
a lieu : voir `frontend/src/components/__tests__/markdown-sanitization.spec.ts`.

Chaque test porte le marqueur `securite` : `pytest -m securite` rejoue la
seule campagne de sécurité, qui est bloquante pour la livraison.
"""
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import select, text

from app.extension import limiter
from database.db import Base, Document, SessionLocal, UserSession, engine
from tests.conftest import MDP_VALIDE

pytestmark = pytest.mark.securite

BACKEND_ROOT = Path(__file__).resolve().parents[2]


# ── TSEC-06 · Injection SQL ──────────────────────────────────────────────────

@pytest.mark.parametrize(
    "charge",
    [
        "' OR '1'='1",
        "'; DROP TABLE document; --",
        "1' UNION SELECT mdp_hash FROM user --",
        'Robert"); DROP TABLE document;--',
    ],
)
def test_tsec06_une_charge_sql_est_traitee_comme_du_texte(client, auth, charge):
    """
    L'ORM paramètre toutes les requêtes : une charge d'injection est stockée
    telle quelle, comme n'importe quelle chaîne, et la table survit.
    """
    reponse = client.post("/documents", json={"titre": charge}, headers=auth)
    assert reponse.status_code == 201
    assert reponse.get_json()["titre"] == charge

    with SessionLocal() as session:
        document = session.execute(select(Document)).scalar_one()
        assert document.titre == charge
        # La table existe toujours : la requête n'a pas été interprétée.
        assert session.execute(text("SELECT COUNT(*) FROM document")).scalar_one() == 1


def test_tsec06b_une_charge_sql_en_parametre_d_url_ne_casse_rien(client, auth):
    reponse = client.get("/documents?id_dossier=' OR '1'='1", headers=auth)
    assert reponse.status_code == 404, "le dossier n'existe pas, la requête reste saine"


# ── TSEC-07 · Aucun secret en clair en base ──────────────────────────────────

def test_tsec07_la_base_ne_contient_aucun_jeton_ni_mot_de_passe_en_clair(
    client, utilisateur
):
    """
    RG-10 — une fuite de la base ne doit permettre ni de rejouer une session,
    ni de retrouver un mot de passe.
    """
    client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    client.post("/auth/forgot-password", json={"email": "camille@exemple.fr"})

    # Les tables sont prises dans les métadonnées SQLAlchemy et interrogées
    # par `select(table)` : aucun nom n'est interpolé dans une chaîne SQL.
    # Un test de sécurité qui construirait lui-même du SQL par f-string
    # donnerait le mauvais exemple, même si les noms de tables viennent du
    # schéma et non d'une entrée utilisateur.
    contenu = ""
    with engine.connect() as connexion:
        for table in Base.metadata.sorted_tables:
            for ligne in connexion.execute(select(table)).all():
                contenu += " ".join(str(valeur) for valeur in ligne)

    assert MDP_VALIDE not in contenu, "le mot de passe apparaît en clair en base"

    jeton_cookie = client.get_cookie("refresh_token", path="/auth").value
    assert jeton_cookie not in contenu, "le jeton de rafraîchissement apparaît en clair en base"


# ── TSEC-08 · Rejeu de session ───────────────────────────────────────────────

def test_tsec08_un_jeton_de_rafraichissement_rejoue_invalide_la_session(
    client, utilisateur
):
    client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    ancien = client.get_cookie("refresh_token", path="/auth").value
    client.post("/auth/refresh")

    client.set_cookie("refresh_token", ancien, path="/auth")
    assert client.post("/auth/refresh").status_code == 401

    with SessionLocal() as session:
        assert session.execute(select(UserSession)).scalars().all() == []


# ── TSEC-09 · Échec sécurisé au démarrage ────────────────────────────────────

def test_tsec09_l_application_refuse_de_demarrer_sans_cle_de_signature():
    """
    Sans JWT_SECRET_KEY, l'application doit échouer bruyamment plutôt que de
    se replier sur une clé de secours : une clé en dur dans le dépôt
    permettrait à quiconque le lit de forger un jeton valide pour n'importe
    quel compte.

    Le test s'exécute dans un sous-processus : app/config.py lève à l'import,
    et ce module est déjà chargé dans le processus de test.
    """
    resultat = subprocess.run(
        [sys.executable, "-c", "import app.config"],
        cwd=BACKEND_ROOT,
        env={"PATH": "/usr/bin:/bin", "HELPMEDRAFT_DB_URL": "sqlite://"},
        capture_output=True,
        text=True,
    )
    assert resultat.returncode != 0, "l'application a démarré sans clé de signature"
    assert "JWT_SECRET_KEY" in resultat.stderr


# ── TSEC-10 · CSRF ───────────────────────────────────────────────────────────

def test_tsec10_le_cookie_de_session_est_protege_contre_le_csrf(client, utilisateur):
    reponse = client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    entete = reponse.headers["Set-Cookie"]

    assert "SameSite=Strict" in entete
    assert "HttpOnly" in entete
    assert "Path=/auth" in entete


def test_le_cookie_est_marque_secure_hors_developpement(app, client, utilisateur, monkeypatch):
    """
    En dehors du développement, le jeton ne doit jamais pouvoir transiter en
    clair sur HTTP (OWASP A02:2021).
    """
    monkeypatch.setitem(app.config, "COOKIE_SECURE", True)
    reponse = client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    assert "Secure" in reponse.headers["Set-Cookie"]


# ── TSEC-11 · Accès horizontal ───────────────────────────────────────────────

def test_tsec11_aucune_ressource_d_autrui_n_est_accessible(
    client, auth, autre_utilisateur, creer_document, creer_dossier
):
    """
    Parcours de toutes les routes portant un identifiant de ressource, avec
    l'identifiant réel d'un tiers. Attendu partout : 404, jamais 403 ni 200.
    """
    document_tiers = creer_document(autre_utilisateur)
    dossier_tiers = creer_dossier(autre_utilisateur)

    appels = [
        client.get(f"/documents/{document_tiers}", headers=auth),
        client.put(f"/documents/{document_tiers}", json={"titre": "X"}, headers=auth),
        client.delete(f"/documents/{document_tiers}", headers=auth),
        client.delete(f"/dossiers/{dossier_tiers}", headers=auth),
        client.get(f"/documents/{document_tiers}/ia/historique", headers=auth),
        client.post(
            f"/documents/{document_tiers}/ia/generer",
            json={"type_action": "reformuler", "scope": "selection", "contenu": "x"},
            headers=auth,
        ),
        client.get(f"/documents?id_dossier={dossier_tiers}", headers=auth),
    ]

    for reponse in appels:
        assert reponse.status_code == 404, (
            f"{reponse.request.method} {reponse.request.path} a répondu "
            f"{reponse.status_code} au lieu de 404"
        )


# ── TSEC-12 · Escalade de privilèges ─────────────────────────────────────────

def test_tsec12_un_jeton_standard_ne_donne_pas_acces_au_back_office(
    client, auth, administrateur
):
    for reponse in (
        client.get("/admin/users", headers=auth),
        client.get("/admin/stats", headers=auth),
        client.delete(f"/admin/users/{administrateur}", headers=auth),
    ):
        assert reponse.status_code == 403


def test_promouvoir_un_compte_ne_passe_pas_par_l_api_publique(client, auth, utilisateur):
    """
    Le rôle n'est pas un champ modifiable par l'utilisateur : il n'existe
    aucune route publique permettant de se promouvoir administrateur.
    """
    from database.db import User

    client.put("/documents/x", json={"role": "admin"}, headers=auth)
    with SessionLocal() as session:
        assert session.get(User, utilisateur).role == "user"


# ── TSEC-13 · Intégrité référentielle ────────────────────────────────────────

def test_tsec13_les_cles_etrangeres_sont_appliquees_par_le_sgbd():
    """
    SQLite n'applique pas les contraintes de clé étrangère par défaut : sans
    le PRAGMA posé à la connexion, le ON DELETE SET NULL de
    Document.id_dossier ne s'exécuterait jamais, et supprimer un dossier
    laisserait des documents pointant vers une ligne inexistante.
    """
    with engine.connect() as connexion:
        assert connexion.execute(text("PRAGMA foreign_keys")).scalar_one() == 1


# ── TSEC-14 · Limitation de débit (KAN-95) ───────────────────────────────────

def test_tsec14_le_rafraichissement_est_limite_en_debit(app, client, utilisateur):
    """
    `/auth/refresh` n'avait aucune limite, contrairement à /register, /login et
    /forgot-password. Le jeton faisant 64 octets aléatoires, la limite ne
    protège pas le secret — elle borne l'usage de la route : épuisement de
    ressources, et martèlement automatisé si un cookie fuit.

    La limitation est désactivée par la fixture `app` pour tous les autres
    tests ; elle est réactivée ici, puis remise dans son état initial.
    """
    client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    limiter.enabled = True
    try:
        codes = [client.post("/auth/refresh").status_code for _ in range(35)]
    finally:
        limiter.enabled = False
        limiter.reset()

    assert 429 in codes, "aucune limite de débit n'est appliquée sur /auth/refresh"
    assert codes.index(429) > 25, (
        f"la limite se déclenche au {codes.index(429) + 1}ᵉ appel, trop tôt pour "
        "un usage normal avec plusieurs onglets"
    )


# ── TSEC-15 · Clé de session Flask ───────────────────────────────────────────

def test_tsec15_l_application_refuse_de_demarrer_sans_cle_de_session():
    """
    Pendant du test TSEC-09 pour SECRET_KEY. Flask s'en sert pour signer les
    cookies de session et les messages flash ; une clé absente ferait échouer
    silencieusement le premier usage ajouté.
    """
    resultat = subprocess.run(
        [sys.executable, "-c", "import app.config"],
        cwd=BACKEND_ROOT,
        env={
            "PATH": "/usr/bin:/bin",
            "HELPMEDRAFT_DB_URL": "sqlite://",
            "JWT_SECRET_KEY": "une-cle-jwt-presente",
        },
        capture_output=True,
        text=True,
    )
    assert resultat.returncode != 0, "l'application a démarré sans clé de session"
    assert "SECRET_KEY" in resultat.stderr


def test_tsec15b_les_deux_cles_sont_distinctes(app):
    """
    Réutiliser une même clé pour signer les jetons d'accès et les cookies de
    session ferait qu'une fuite sur l'un compromet l'autre.
    """
    assert app.config["SECRET_KEY"] != app.config["JWT_SECRET_KEY"]
