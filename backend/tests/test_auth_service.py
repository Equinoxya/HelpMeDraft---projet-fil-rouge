"""
Tests unitaires du composant métier le plus sensible : auth_service.
Couvre TU-09 à TU-15 du § 9.3.3, plus la politique de mot de passe (§ 7.2.1)
et le hachage des refresh tokens (§ 7.2.2).

Ces tests n'ouvrent aucune route : ils exercent directement les fonctions, ce
que permet la séparation en couches du § 5.2.2.
"""

import datetime
import hashlib

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

MDP = "MotDePasse1"


# ── Mots de passe (TU-09, TU-10, TU-11) ──────────────────────────────────────
def test_tu09_mot_de_passe_correct_accepte():
    assert verify_password(MDP, hash_password(MDP)) is True


def test_tu10_mot_de_passe_errone_refuse():
    assert verify_password("MauvaisMdp1", hash_password(MDP)) is False


def test_tu11_le_sel_est_aleatoire():
    """Deux hachages du même mot de passe doivent différer.

    C'est la propriété qui rend une table précalculée inutile : si les deux
    empreintes étaient égales, bcrypt serait utilisé sans sel et deux comptes
    partageant un mot de passe seraient reconnaissables dans un dump.
    """
    a, b = hash_password(MDP), hash_password(MDP)
    assert a != b
    assert verify_password(MDP, a) and verify_password(MDP, b)


def test_le_hachage_ne_contient_jamais_le_mot_de_passe():
    assert MDP not in hash_password(MDP)


@pytest.mark.parametrize(
    "mdp,attendu",
    [
        ("MotDePasse1", True),  # 8+ car., majuscule, minuscule, chiffre
        ("Mdp1", False),  # trop court
        ("motdepasse1", False),  # pas de majuscule
        ("MOTDEPASSE1", False),  # pas de minuscule
        ("MotDePasse", False),  # pas de chiffre
        ("Aa1aaaaa", True),  # exactement 8 caractères : borne acceptée
        ("Aa1aaaa", False),  # 7 caractères : borne refusée
    ],
)
def test_politique_de_mot_de_passe(mdp, attendu):
    """La politique n'exige pas de caractère spécial : choix assumé (§ 7.2.1).

    Le test verrouille les quatre règles retenues ET l'absence de la cinquième :
    si quelqu'un ajoutait une exigence de symbole, « MotDePasse1 » casserait et
    la décision documentée serait revue sciemment, pas par inadvertance.
    """
    assert is_password_valid(mdp) is attendu


def test_un_mot_de_passe_sans_symbole_reste_valide():
    assert is_password_valid("MotDePasse1") is True


# ── Access tokens (TU-12 à TU-15) ────────────────────────────────────────────
def test_tu12_access_token_valide_restitue_le_user_id(ctx):
    token = generate_access_token("u-123")
    assert decode_access_token(token)["sub"] == "u-123"


def test_tu13_access_token_expire_est_rejete(ctx):
    """Jeton correctement signé mais périmé : il doit être refusé.

    On forge le jeton avec la vraie clé et un `exp` dans le passé, plutôt que
    d'attendre 15 minutes.
    """
    passe = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=1)
    token = jwt.encode(
        {"sub": "u-123", "iat": passe - datetime.timedelta(minutes=15), "exp": passe},
        ctx.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )
    with pytest.raises(ValueError):
        decode_access_token(token)


def test_tu14_jeton_signe_avec_une_autre_cle_est_rejete(ctx):
    """Sans cette propriété, la clé secrète ne servirait à rien : n'importe qui
    pourrait forger un jeton pour n'importe quel user_id (§ 6.3)."""
    maintenant = datetime.datetime.now(datetime.UTC)
    token = jwt.encode(
        {"sub": "u-123", "iat": maintenant, "exp": maintenant + datetime.timedelta(minutes=15)},
        "une-autre-cle-que-celle-de-l-application",
        algorithm="HS256",
    )
    with pytest.raises(ValueError):
        decode_access_token(token)


def test_tu15_jeton_en_algorithme_none_est_rejete(ctx):
    """Confusion d'algorithme — classe d'attaque relevée en veille (§ 11.2).

    Un vérificateur qui fait confiance à l'en-tête `alg` du jeton accepte un
    jeton NON SIGNÉ présenté en `alg: none`. Le projet passe
    `algorithms=["HS256"]` explicitement, donc refuse. Le test rend cette
    propriété permanente au lieu d'une vérification ponctuelle : si quelqu'un
    retirait l'argument un jour, l'authentification tomberait entièrement et
    ce test serait le seul à le signaler.
    """
    maintenant = datetime.datetime.now(datetime.UTC)
    token = jwt.encode(
        {"sub": "u-123", "iat": maintenant, "exp": maintenant + datetime.timedelta(minutes=15)},
        key="",
        algorithm="none",
    )
    with pytest.raises(ValueError):
        decode_access_token(token)


def test_un_jeton_malforme_est_rejete(ctx):
    with pytest.raises(ValueError):
        decode_access_token("ceci-n-est-pas-un-jeton")


# ── Refresh tokens (§ 7.2.2) ─────────────────────────────────────────────────
def test_les_refresh_tokens_sont_uniques_et_longs():
    jetons = {generate_refresh_token() for _ in range(50)}
    assert len(jetons) == 50  # aucun doublon
    assert all(len(j) > 60 for j in jetons)  # 64 octets encodés en url-safe


def test_l_empreinte_du_refresh_token_est_un_sha256():
    """SHA-256 sans sel est le bon choix ICI, contrairement au mot de passe :
    le jeton est un aléa de 64 octets, donc hors de portée d'un dictionnaire
    (§ 7.2.2). Le test fixe l'algorithme attendu."""
    jeton = generate_refresh_token()
    empreinte = hash_refresh_token(jeton)
    assert empreinte == hashlib.sha256(jeton.encode()).hexdigest()
    assert len(empreinte) == 64
    assert empreinte != jeton


def test_la_meme_empreinte_pour_le_meme_jeton():
    """Propriété indispensable : la vérification hache le jeton présenté et
    compare. Sans déterminisme, aucune session ne serait retrouvable."""
    jeton = generate_refresh_token()
    assert hash_refresh_token(jeton) == hash_refresh_token(jeton)
