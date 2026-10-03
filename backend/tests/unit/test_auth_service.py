"""
Tests unitaires du service d'authentification — TU-01 à TU-08.

Couvre les primitives sur lesquelles repose toute la sécurité des comptes :
hachage des mots de passe, émission et vérification des jetons d'accès,
empreinte des jetons de rafraîchissement.
"""

import datetime

import jwt
import pytest

from app.services.auth_service import (
    decode_access_token,
    generate_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    is_password_valid,
    verify_password,
)

# ── Mots de passe ────────────────────────────────────────────────────────────


def test_tu01_hash_password_ne_renvoie_pas_le_clair():
    empreinte = hash_password("MotDePasse1")
    assert empreinte != "MotDePasse1"
    assert empreinte.startswith("$2b$"), "l'empreinte doit être au format bcrypt"


def test_tu02_verify_password_accepte_le_bon_mot_de_passe():
    assert verify_password("MotDePasse1", hash_password("MotDePasse1")) is True


def test_tu03_verify_password_refuse_un_mauvais_mot_de_passe():
    assert verify_password("MauvaisMdp1", hash_password("MotDePasse1")) is False


def test_tu04_deux_hachages_du_meme_mot_de_passe_different():
    """
    Le sel bcrypt est tiré au hasard à chaque appel. Deux empreintes
    identiques signaleraient un sel constant : une table arc-en-ciel
    construite une fois casserait alors tous les comptes d'un coup.
    """
    assert hash_password("MotDePasse1") != hash_password("MotDePasse1")


@pytest.mark.parametrize("mdp", ["MotDePasse1", "Abcdefg1", "LongMotDePasse2026"])
def test_is_password_valid_accepte_les_mots_de_passe_conformes(mdp):
    assert is_password_valid(mdp) is True


@pytest.mark.parametrize(
    "mdp, raison",
    [
        ("Court1", "moins de 8 caractères"),
        ("motdepasse1", "pas de majuscule"),
        ("MOTDEPASSE1", "pas de minuscule"),
        ("MotDePasse", "pas de chiffre"),
    ],
)
def test_is_password_valid_refuse_les_mots_de_passe_faibles(mdp, raison):
    assert is_password_valid(mdp) is False, f"devrait être refusé : {raison}"


# ── Jetons d'accès ───────────────────────────────────────────────────────────


def test_tu05_generate_access_token_produit_un_jwt_decodable(app):
    with app.app_context():
        jeton = generate_access_token("utilisateur-123")
        charge = decode_access_token(jeton)
    assert charge["sub"] == "utilisateur-123"
    assert "exp" in charge


def test_tu06_decode_access_token_refuse_un_jeton_expire(app):
    passe = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=1)
    with app.app_context():
        jeton_expire = jwt.encode(
            {"sub": "utilisateur-123", "exp": passe},
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )
        with pytest.raises(ValueError, match="expiré"):
            decode_access_token(jeton_expire)


def test_tu07_decode_access_token_refuse_une_signature_etrangere(app):
    """
    Un jeton signé avec une autre clé doit être rejeté. Sans cette
    vérification, n'importe qui pourrait forger un jeton pour n'importe quel
    user_id et usurper une identité.
    """
    futur = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
    jeton_etranger = jwt.encode(
        {"sub": "attaquant", "exp": futur}, "une-autre-cle", algorithm="HS256"
    )
    with app.app_context():
        with pytest.raises(ValueError):
            decode_access_token(jeton_etranger)


def test_decode_access_token_refuse_un_jeton_malforme(app):
    with app.app_context():
        with pytest.raises(ValueError):
            decode_access_token("ceci-n-est-pas-un-jeton")


# ── Jetons de rafraîchissement ───────────────────────────────────────────────


def test_tu08_hash_refresh_token_est_un_sha256_deterministe():
    empreinte = hash_refresh_token("jeton-de-rafraichissement")
    assert len(empreinte) == 64
    assert all(c in "0123456789abcdef" for c in empreinte)
    assert empreinte == hash_refresh_token("jeton-de-rafraichissement")


def test_hash_refresh_token_distingue_deux_jetons():
    assert hash_refresh_token("jeton-a") != hash_refresh_token("jeton-b")


def test_generate_refresh_token_produit_un_secret_non_devinable():
    jetons = {generate_refresh_token() for _ in range(50)}
    assert len(jetons) == 50, "deux jetons identiques sur 50 tirages"
    assert all(len(j) >= 64 for j in jetons)
