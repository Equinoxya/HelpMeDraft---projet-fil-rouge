# -*- coding: utf-8 -*-
"""
Tests d'intégration de la chaîne d'authentification (§ 9.4).

Ils exercent les routes de bout en bout, base incluse. La zone est celle où une
régression compromet TOUS les comptes : c'est pourquoi elle reçoit l'essentiel
de l'effort (§ 9.1).

Plusieurs de ces tests ne vérifient pas un code HTTP mais une DÉCISION DE
CONCEPTION — ce qui est stocké en base, l'égalité de deux réponses, la
révocation en cascade. Ce sont les plus utiles : un test qui se contente de
constater un 200 passerait aussi sur une implémentation défaillante.
"""
import hashlib
from datetime import timedelta

from database.db import SessionLocal, UserSession
from utilitaires import utc_now_naive


def cookie_de(client):
    return client.get_cookie("refresh_token", path="/auth")


# ── Inscription ──────────────────────────────────────────────────────────────
def test_inscription_cree_le_compte_et_le_consentement(client):
    """L'inscription INCLUT le recueil du consentement (§ 5.6.3) : les deux
    lignes sont écrites dans la même transaction, ou aucune."""
    reponse = client.post("/auth/register", json={
        "lastname": "Bellissens", "firstname": "Ophelie",
        "email": "nouvelle@example.test", "mdp": "MotDePasse1",
        "rgpd_consent": True,
    })
    assert reponse.status_code == 201
    from database.db import Consentement, User
    with SessionLocal() as db:
        user = db.query(User).filter_by(email="nouvelle@example.test").one()
        consentements = db.query(Consentement).filter_by(user_id=user.user_id).all()
    assert len(consentements) == 1
    assert consentements[0].accepte is True
    assert consentements[0].type_consentement == "rgpd"


def test_inscription_refusee_sans_consentement(client):
    reponse = client.post("/auth/register", json={
        "lastname": "X", "firstname": "Y", "email": "sans-consentement@example.test",
        "mdp": "MotDePasse1", "rgpd_consent": False,
    })
    assert reponse.status_code == 400
    from database.db import User
    with SessionLocal() as db:
        assert db.query(User).filter_by(email="sans-consentement@example.test").first() is None


def test_inscription_refusee_si_mot_de_passe_non_conforme(client):
    reponse = client.post("/auth/register", json={
        "lastname": "X", "firstname": "Y", "email": "faible@example.test",
        "mdp": "motdepasse", "rgpd_consent": True,
    })
    assert reponse.status_code == 400


def test_le_mot_de_passe_n_est_jamais_stocke_en_clair(client, compte):
    from database.db import User
    with SessionLocal() as db:
        user = db.query(User).filter_by(email=compte["email"]).one()
    assert "MotDePasse1" not in user.mdp_hash
    assert user.mdp_hash.startswith("$2")          # empreinte bcrypt


def test_adresse_deja_utilisee_renvoie_409_ecart_documente(client, compte):
    """ÉCART CONNU, écart n° 1 du § 8.11 — et le test l'assume comme tel.

    La route révèle qu'une adresse est déjà enregistrée, ce qui permet d'énumérer
    les comptes. C'est incohérent avec /login et /forgot-password, qui répondent
    de façon indiscernable. Le test fige le comportement ACTUEL (409) pour que la
    correction soit un choix explicite : le jour où la route renverra 201, ce test
    échouera et devra être réécrit — ce qui est exactement le signal voulu.
    """
    reponse = client.post("/auth/register", json={
        "lastname": "Test", "firstname": "Doublon",
        "email": compte["email"], "mdp": "MotDePasse1", "rgpd_consent": True,
    })
    assert reponse.status_code == 409


# ── Connexion ────────────────────────────────────────────────────────────────
def test_connexion_pose_un_cookie_correctement_attribue(client, compte):
    reponse = client.post("/auth/login",
                          json={"email": compte["email"], "mdp": compte["mdp"]})
    assert reponse.status_code == 200
    assert "access_token" in reponse.get_json()

    entete = reponse.headers.get("Set-Cookie", "")
    # Chaque attribut répond à une menace distincte (§ 7.4.3).
    assert "HttpOnly" in entete                   # un XSS ne lit pas le jeton
    assert "Path=/auth" in entete                 # portée minimale
    assert "SameSite=Strict" in entete            # CSRF sur /auth/refresh
    # APP_ENV=development : Secure absent, sinon le cookie ne passerait pas
    # sur http://localhost et l'authentification serait cassée en dev (§ 6.3).
    assert "Secure" not in entete


def test_en_base_on_stocke_l_empreinte_pas_le_jeton(client, compte):
    """LE test de la correction du § 5.4.7.

    Une fuite de la base (dump, sauvegarde mal protégée, injection en lecture)
    ne doit pas permettre de rejouer une session active. On vérifie donc que la
    valeur enregistrée est l'empreinte du cookie, et non le cookie.
    """
    client.post("/auth/login", json={"email": compte["email"], "mdp": compte["mdp"]})
    jeton_clair = cookie_de(client).value
    with SessionLocal() as db:
        stocke = db.query(UserSession).one().refresh_token_hash
    assert stocke == hashlib.sha256(jeton_clair.encode()).hexdigest()
    assert stocke != jeton_clair


def test_mot_de_passe_errone_et_compte_inexistant_sont_indiscernables(client, compte):
    """Anti-énumération (§ 8.8) : le test compare les CORPS, pas seulement les
    codes. Deux 401 porteurs de messages différents rétabliraient la fuite."""
    mauvais_mdp = client.post("/auth/login",
                              json={"email": compte["email"], "mdp": "MauvaisMdp1"})
    inconnu = client.post("/auth/login",
                          json={"email": "jamais-vu@example.test", "mdp": "MotDePasse1"})
    assert mauvais_mdp.status_code == inconnu.status_code == 401
    assert mauvais_mdp.get_json() == inconnu.get_json()


# ── Rotation du refresh token (§ 7.2.2) ──────────────────────────────────────
def test_refresh_fait_tourner_le_jeton(client, connecte):
    ancien = connecte["refresh"]
    reponse = client.post("/auth/refresh")
    assert reponse.status_code == 200
    nouveau = cookie_de(client).value
    assert nouveau != ancien, "le jeton doit changer à chaque usage"

    with SessionLocal() as db:
        empreintes = {(s.refresh_token_hash, s.revoke) for s in db.query(UserSession).all()}
    # L'ancien est marqué consommé, le nouveau est actif.
    assert (hashlib.sha256(ancien.encode()).hexdigest(), True) in empreintes
    assert (hashlib.sha256(nouveau.encode()).hexdigest(), False) in empreintes


def test_rejouer_un_jeton_consomme_revoque_toutes_les_sessions(client, connecte):
    """Le test le plus important du fichier.

    Si un jeton déjà consommé se présente, deux acteurs détiennent le même
    secret à usage unique : impossible de savoir lequel est légitime. La seule
    réponse sûre est de couper TOUTES les sessions du compte (§ 7.2.2).

    Un test qui se contenterait d'un 401 passerait sur une implémentation qui
    refuse la requête sans révoquer — c'est-à-dire qui laisse le voleur en place.
    D'où la vérification de l'état de la base.
    """
    ancien = connecte["refresh"]
    client.post("/auth/refresh")                   # l'ancien jeton est consommé

    client.set_cookie("refresh_token", ancien, path="/auth")
    rejeu = client.post("/auth/refresh")

    assert rejeu.status_code == 401
    with SessionLocal() as db:
        assert db.query(UserSession).count() == 0, \
            "la réutilisation doit révoquer toutes les sessions, pas seulement refuser"


def test_refresh_sans_cookie_est_refuse(client):
    assert client.post("/auth/refresh").status_code == 401


def test_refresh_avec_un_jeton_inconnu_est_refuse(client):
    client.set_cookie("refresh_token", "jeton-qui-n-a-jamais-existe", path="/auth")
    assert client.post("/auth/refresh").status_code == 401


def test_refresh_token_expire_est_refuse_et_la_session_supprimee(client, connecte):
    """On vieillit la session en base plutôt que d'attendre sept jours."""
    with SessionLocal() as db:
        session = db.query(UserSession).one()
        session.refresh_token_exp = utc_now_naive() - timedelta(minutes=1)
        db.commit()

    reponse = client.post("/auth/refresh")
    assert reponse.status_code == 401
    with SessionLocal() as db:
        assert db.query(UserSession).count() == 0


# ── Déconnexion et route protégée ────────────────────────────────────────────
def test_logout_supprime_la_session_en_base(client, connecte):
    assert client.post("/auth/logout").status_code == 200
    with SessionLocal() as db:
        assert db.query(UserSession).count() == 0


def test_me_exige_un_jeton(client):
    assert client.get("/auth/me").status_code == 401


def test_me_refuse_un_jeton_invalide(client):
    assert client.get("/auth/me",
                      headers={"Authorization": "Bearer pas-un-jeton"}).status_code == 401


def test_me_renvoie_le_profil_et_jamais_l_empreinte(client, connecte):
    reponse = client.get("/auth/me", headers=connecte["headers"])
    assert reponse.status_code == 200
    corps = reponse.get_json()
    assert corps["email"] == "test@example.test"
    assert corps["role"] == "user"
    # Une route de profil ne doit pas laisser fuiter l'empreinte du mot de passe.
    assert "mdp_hash" not in corps and "mdp" not in corps


# ── Réinitialisation de mot de passe ─────────────────────────────────────────
def test_forgot_password_repond_pareil_que_l_adresse_existe_ou_non(client, compte):
    """Même raisonnement anti-énumération que sur /login (§ 8.8)."""
    connue = client.post("/auth/forgot-password", json={"email": compte["email"]})
    inconnue = client.post("/auth/forgot-password",
                           json={"email": "jamais-vu@example.test"})
    assert connue.status_code == inconnue.status_code == 200
    assert connue.get_json() == inconnue.get_json()


def test_reset_password_revoque_les_sessions_ouvertes(client, compte, connecte):
    """Changer son mot de passe après une compromission ne sert à rien si les
    sessions ouvertes par l'attaquant survivent (§ 8.2). On crée une demande de
    réinitialisation en base, on l'utilise, et on vérifie que la session tombe.
    """
    from app.services.auth_service import generate_reset_token
    from database.db import PasswordReset

    jeton_clair, empreinte = generate_reset_token()
    with SessionLocal() as db:
        db.add(PasswordReset(user_id=connecte["user_id"], token_hash=empreinte,
                             expires_at=utc_now_naive() + timedelta(hours=1)))
        db.commit()
        assert db.query(UserSession).count() == 1   # une session est bien ouverte

    reponse = client.post("/auth/reset-password",
                          json={"token": jeton_clair, "mdp": "NouveauMdp1"})
    assert reponse.status_code == 200

    with SessionLocal() as db:
        assert db.query(UserSession).count() == 0, "les sessions doivent être révoquées"
        assert db.query(PasswordReset).one().used is True

    # L'ancien mot de passe ne fonctionne plus, le nouveau fonctionne.
    assert client.post("/auth/login",
                       json={"email": compte["email"], "mdp": "MotDePasse1"}).status_code == 401
    assert client.post("/auth/login",
                       json={"email": compte["email"], "mdp": "NouveauMdp1"}).status_code == 200


def test_un_jeton_de_reinitialisation_ne_sert_qu_une_fois(client, compte):
    from app.services.auth_service import generate_reset_token
    from database.db import PasswordReset

    jeton_clair, empreinte = generate_reset_token()
    with SessionLocal() as db:
        db.add(PasswordReset(user_id=compte["user_id"], token_hash=empreinte,
                             expires_at=utc_now_naive() + timedelta(hours=1)))
        db.commit()

    premier = client.post("/auth/reset-password",
                          json={"token": jeton_clair, "mdp": "NouveauMdp1"})
    second = client.post("/auth/reset-password",
                         json={"token": jeton_clair, "mdp": "EncoreAutre1"})
    assert premier.status_code == 200
    assert second.status_code == 400


def test_un_jeton_de_reinitialisation_expire_est_refuse(client, compte):
    from app.services.auth_service import generate_reset_token
    from database.db import PasswordReset

    jeton_clair, empreinte = generate_reset_token()
    with SessionLocal() as db:
        db.add(PasswordReset(user_id=compte["user_id"], token_hash=empreinte,
                             expires_at=utc_now_naive() - timedelta(minutes=1)))
        db.commit()

    reponse = client.post("/auth/reset-password",
                          json={"token": jeton_clair, "mdp": "NouveauMdp1"})
    assert reponse.status_code == 400
