"""
Tests d'intégration des routes d'authentification — TI-01 à TI-14.

Chaque test traverse la pile complète : HTTP → contrôleur → service → base.
"""
from sqlalchemy import select

from database.db import PasswordReset, SessionLocal, User, UserSession
from tests.conftest import MDP_VALIDE

INSCRIPTION = {
    "email": "nouveau@exemple.fr",
    "mdp": MDP_VALIDE,
    "lastname": "Martin",
    "firstname": "Alex",
    "rgpd_consent": True,
}


# ── Inscription ──────────────────────────────────────────────────────────────

def test_ti01_inscription_cree_le_compte_et_trace_le_consentement(client):
    reponse = client.post("/auth/register", json=INSCRIPTION)
    assert reponse.status_code == 201

    with SessionLocal() as session:
        utilisateur = session.execute(
            select(User).where(User.email == "nouveau@exemple.fr")
        ).scalar_one()
        assert utilisateur.mdp_hash != MDP_VALIDE, "le mot de passe ne doit jamais être stocké en clair"
        assert utilisateur.role == "user", "le rôle par défaut ne doit pas être administrateur"
        assert len(utilisateur.consentements) == 1, "le consentement RGPD doit être tracé en base"
        assert utilisateur.consentements[0].accepte is True


def test_ti02_inscription_refuse_une_adresse_deja_prise(client, utilisateur):
    reponse = client.post("/auth/register", json={**INSCRIPTION, "email": "camille@exemple.fr"})
    assert reponse.status_code == 409

    with SessionLocal() as session:
        comptes = session.execute(
            select(User).where(User.email == "camille@exemple.fr")
        ).scalars().all()
    assert len(comptes) == 1, "aucun doublon ne doit être créé"


def test_ti02b_inscription_revele_l_existence_du_compte(client, utilisateur):
    """
    Constat, pas validation. La route répond 409 « Cet email est déjà
    utilisé » : un attaquant peut donc énumérer les comptes enregistrés en
    bouclant sur des adresses. Comparer avec /auth/forgot-password (TI-14),
    qui répond volontairement la même chose dans les deux cas.

    Ce test fige le comportement actuel pour qu'il soit visible, pas pour
    l'approuver. Il devra être inversé quand KAN-94 sera traité.
    """
    existant = client.post("/auth/register", json={**INSCRIPTION, "email": "camille@exemple.fr"})
    inconnu = client.post("/auth/register", json=INSCRIPTION)
    assert existant.status_code != inconnu.status_code, (
        "si ces codes deviennent identiques, KAN-94 est corrigé : inverser ce test"
    )


def test_ti03_inscription_refuse_un_champ_manquant(client):
    for champ in ("email", "mdp", "lastname", "firstname"):
        charge = {k: v for k, v in INSCRIPTION.items() if k != champ}
        assert client.post("/auth/register", json=charge).status_code == 400, champ


def test_inscription_refuse_sans_consentement_rgpd(client):
    reponse = client.post("/auth/register", json={**INSCRIPTION, "rgpd_consent": False})
    assert reponse.status_code == 400


def test_inscription_refuse_un_mot_de_passe_faible(client):
    reponse = client.post("/auth/register", json={**INSCRIPTION, "mdp": "faible"})
    assert reponse.status_code == 400


# ── Connexion ────────────────────────────────────────────────────────────────

def test_ti04_connexion_valide_rend_un_jeton_et_ouvre_une_session(client, utilisateur):
    reponse = client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    assert reponse.status_code == 200

    corps = reponse.get_json()
    assert corps["access_token"]
    assert corps["user"]["email"] == "camille@exemple.fr"
    assert "mdp_hash" not in corps["user"], "l'empreinte ne doit jamais sortir de l'API"

    with SessionLocal() as session:
        sessions = session.execute(
            select(UserSession).where(UserSession.user_id == utilisateur)
        ).scalars().all()
    assert len(sessions) == 1


def test_ti05_ti06_connexion_invalide_rend_un_message_indifferencie(client, utilisateur):
    """
    Mot de passe erroné et compte inexistant doivent produire exactement la
    même réponse. Toute différence — code, message, voire temps de réponse —
    permet de savoir quelles adresses sont enregistrées.
    """
    mauvais_mdp = client.post(
        "/auth/login", json={"email": "camille@exemple.fr", "mdp": "MauvaisMdp1"}
    )
    compte_inconnu = client.post(
        "/auth/login", json={"email": "personne@exemple.fr", "mdp": MDP_VALIDE}
    )

    assert mauvais_mdp.status_code == compte_inconnu.status_code == 401
    assert mauvais_mdp.get_json() == compte_inconnu.get_json()


def test_connexion_refuse_un_champ_manquant(client, utilisateur):
    assert client.post("/auth/login", json={"email": "camille@exemple.fr"}).status_code == 400
    assert client.post("/auth/login", json={"mdp": MDP_VALIDE}).status_code == 400


def test_ti07_le_cookie_de_rafraichissement_porte_les_bons_attributs(client, utilisateur):
    reponse = client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    entete = reponse.headers["Set-Cookie"]

    assert "HttpOnly" in entete, "sans HttpOnly, un XSS exfiltre le jeton de session longue"
    assert "SameSite=Strict" in entete, "protection CSRF sur /auth/refresh"
    assert "Path=/auth" in entete, "le cookie ne doit pas accompagner toutes les requêtes"


def test_le_jeton_de_rafraichissement_n_est_jamais_stocke_en_clair(client, utilisateur):
    """RG-10 — la base ne contient que l'empreinte SHA-256 du jeton."""
    reponse = client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    jeton_en_clair = reponse.headers["Set-Cookie"].split("refresh_token=")[1].split(";")[0]

    with SessionLocal() as session:
        session_bdd = session.execute(select(UserSession)).scalar_one()

    assert session_bdd.refresh_token_hash != jeton_en_clair
    assert len(session_bdd.refresh_token_hash) == 64


# ── Rafraîchissement et rotation ─────────────────────────────────────────────

def test_ti08_le_rafraichissement_tourne_le_jeton(client, utilisateur):
    client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    ancien = client.get_cookie("refresh_token", path="/auth").value

    reponse = client.post("/auth/refresh")
    assert reponse.status_code == 200
    assert reponse.get_json()["access_token"]

    nouveau = client.get_cookie("refresh_token", path="/auth").value
    assert nouveau != ancien, "le jeton doit être remplacé à chaque usage"


def test_ti09_un_jeton_rejoue_est_refuse(client, utilisateur):
    """
    Détection de rejeu : un jeton déjà tourné qui revient signale un vol.
    La session doit tomber, pas seulement la requête.
    """
    client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})
    ancien = client.get_cookie("refresh_token", path="/auth").value

    client.post("/auth/refresh")                      # rotation : l'ancien devient invalide
    client.set_cookie("refresh_token", ancien, path="/auth")

    reponse = client.post("/auth/refresh")
    assert reponse.status_code == 401

    with SessionLocal() as session:
        restantes = session.execute(
            select(UserSession).where(UserSession.user_id == utilisateur)
        ).scalars().all()
    assert restantes == [], "la session doit être supprimée après détection d'un rejeu"


def test_ti10_le_rafraichissement_sans_cookie_est_refuse(client):
    assert client.post("/auth/refresh").status_code == 401


# ── Déconnexion ──────────────────────────────────────────────────────────────

def test_ti11_la_deconnexion_supprime_la_session(client, utilisateur):
    client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": MDP_VALIDE})

    assert client.post("/auth/logout").status_code == 200

    with SessionLocal() as session:
        assert session.execute(select(UserSession)).scalars().all() == []


def test_la_deconnexion_sans_session_est_refusee(client):
    assert client.post("/auth/logout").status_code == 400


# ── Identité ─────────────────────────────────────────────────────────────────

def test_ti12_me_sans_jeton_est_refuse(client):
    assert client.get("/auth/me").status_code == 401


def test_me_refuse_un_entete_mal_forme(client, auth):
    assert client.get("/auth/me", headers={"Authorization": "Token abc"}).status_code == 401


def test_ti13_me_rend_l_identite_sans_l_empreinte(client, auth):
    reponse = client.get("/auth/me", headers=auth)
    assert reponse.status_code == 200

    corps = reponse.get_json()
    assert corps["email"] == "camille@exemple.fr"
    assert corps["role"] == "user"
    assert "mdp_hash" not in corps


# ── Réinitialisation de mot de passe ─────────────────────────────────────────

def test_ti14_mot_de_passe_oublie_repond_pareil_pour_une_adresse_inconnue(client, utilisateur):
    connue = client.post("/auth/forgot-password", json={"email": "camille@exemple.fr"})
    inconnue = client.post("/auth/forgot-password", json={"email": "personne@exemple.fr"})

    assert connue.status_code == inconnue.status_code == 200
    assert connue.get_json() == inconnue.get_json()

    with SessionLocal() as session:
        demandes = session.execute(select(PasswordReset)).scalars().all()
    assert len(demandes) == 1, "une seule demande, pour le compte qui existe réellement"


def test_le_jeton_de_reinitialisation_n_est_pas_stocke_en_clair(client, utilisateur):
    client.post("/auth/forgot-password", json={"email": "camille@exemple.fr"})
    with SessionLocal() as session:
        demande = session.execute(select(PasswordReset)).scalar_one()
    assert len(demande.token_hash) == 64
    assert demande.used is False


def test_reinitialisation_refuse_un_jeton_inconnu(client, utilisateur):
    reponse = client.post(
        "/auth/reset-password", json={"token": "jeton-invente", "mdp": "NouveauMdp1"}
    )
    assert reponse.status_code == 400


def test_reinitialisation_refuse_un_mot_de_passe_faible(client, utilisateur):
    reponse = client.post("/auth/reset-password", json={"token": "x", "mdp": "faible"})
    assert reponse.status_code == 400
