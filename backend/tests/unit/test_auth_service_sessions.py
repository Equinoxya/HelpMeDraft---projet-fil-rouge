"""
Tests du cycle de vie des sessions — `auth_service`, partie base de données.

Fichier séparé de `test_auth_service.py` : ces fonctions touchent la base,
là où les précédentes sont des primitives pures. Elles restent des tests de
service — elles ne passent pas par HTTP.

Couvre les branches que les tests de routes n'atteignent pas : expiration des
jetons, révocation en cascade, et `verify_refresh_token`, qui n'est appelée
par aucune route aujourd'hui.
"""
from datetime import timedelta

import pytest
from sqlalchemy import select

from app.services.auth_service import (
    REFRESH_TOKEN_EXPIRES_DAYS,
    create_session,
    generate_reset_token,
    hash_refresh_token,
    hash_reset_token,
    is_reset_token_expired,
    purge_expired_sessions,
    revoke_all_user_sessions,
    rotate_refresh_token,
    verify_refresh_token,
)
from database.db import SessionLocal, UserSession
from utilitaires import utc_now_naive


def _perimer(jeton):
    """Antidate l'expiration d'une session pour tester la branche d'expiration."""
    with SessionLocal() as session:
        ligne = session.execute(
            select(UserSession).where(
                UserSession.refresh_token_hash == hash_refresh_token(jeton)
            )
        ).scalar_one()
        ligne.refresh_token_exp = utc_now_naive() - timedelta(seconds=1)
        session.commit()


# ── Création ─────────────────────────────────────────────────────────────────

def test_create_session_enregistre_l_empreinte_et_non_le_jeton(utilisateur):
    jeton = create_session(utilisateur)

    with SessionLocal() as session:
        ligne = session.execute(select(UserSession)).scalar_one()

    assert ligne.refresh_token_hash == hash_refresh_token(jeton)
    assert ligne.refresh_token_hash != jeton
    assert ligne.revoke is False
    assert ligne.refresh_token_exp > utc_now_naive() + timedelta(
        days=REFRESH_TOKEN_EXPIRES_DAYS - 1
    )


# ── Vérification ─────────────────────────────────────────────────────────────

def test_verify_refresh_token_rend_le_proprietaire(utilisateur):
    jeton = create_session(utilisateur)
    assert verify_refresh_token(jeton) == utilisateur


def test_verify_refresh_token_refuse_un_jeton_inconnu(utilisateur):
    with pytest.raises(ValueError, match="invalide"):
        verify_refresh_token("jeton-jamais-emis")


def test_verify_refresh_token_refuse_et_purge_un_jeton_expire(utilisateur):
    jeton = create_session(utilisateur)
    _perimer(jeton)

    with pytest.raises(ValueError, match="expiré"):
        verify_refresh_token(jeton)

    with SessionLocal() as session:
        assert session.execute(select(UserSession)).scalars().all() == [], (
            "une session expirée doit être supprimée, pas seulement refusée"
        )


# ── Rotation ─────────────────────────────────────────────────────────────────

def test_rotate_refresh_token_marque_l_ancienne_session_et_en_cree_une_nouvelle(
    utilisateur,
):
    ancien = create_session(utilisateur)
    proprietaire, nouveau = rotate_refresh_token(ancien)

    assert proprietaire == utilisateur
    assert nouveau != ancien

    with SessionLocal() as session:
        lignes = session.execute(select(UserSession)).scalars().all()
    etats = {l.refresh_token_hash: l.revoke for l in lignes}
    assert etats[hash_refresh_token(ancien)] is True, "l'ancienne session doit être marquée"
    assert etats[hash_refresh_token(nouveau)] is False


def test_rotate_refresh_token_refuse_un_jeton_inconnu(utilisateur):
    with pytest.raises(ValueError, match="invalide"):
        rotate_refresh_token("jeton-jamais-emis")


def test_rotate_refresh_token_refuse_et_purge_un_jeton_expire(utilisateur):
    jeton = create_session(utilisateur)
    _perimer(jeton)

    with pytest.raises(ValueError, match="expiré"):
        rotate_refresh_token(jeton)

    with SessionLocal() as session:
        assert session.execute(select(UserSession)).scalars().all() == []


def test_rejouer_un_jeton_revoque_coupe_toutes_les_sessions(utilisateur):
    """
    Un jeton déjà tourné qui revient signale un vol : on ne sait pas lequel
    des deux porteurs est légitime, donc on invalide tout et on force une
    nouvelle authentification.
    """
    premier = create_session(utilisateur)
    create_session(utilisateur)              # seconde session, autre appareil
    rotate_refresh_token(premier)            # le premier est désormais révoqué

    with pytest.raises(ValueError, match="Réutilisation détectée"):
        rotate_refresh_token(premier)

    with SessionLocal() as session:
        assert session.execute(select(UserSession)).scalars().all() == [], (
            "toutes les sessions du compte doivent tomber, pas seulement la volée"
        )


def test_revoke_all_user_sessions_ne_touche_pas_les_autres_comptes(
    utilisateur, autre_utilisateur
):
    create_session(utilisateur)
    create_session(autre_utilisateur)

    with SessionLocal() as session:
        revoke_all_user_sessions(utilisateur, session)
        session.commit()

    with SessionLocal() as session:
        restantes = session.execute(select(UserSession)).scalars().all()
    assert [l.user_id for l in restantes] == [autre_utilisateur]


# ── Jetons de réinitialisation ───────────────────────────────────────────────

def test_generate_reset_token_rend_un_couple_clair_empreinte():
    clair, empreinte = generate_reset_token()
    assert empreinte == hash_reset_token(clair)
    assert len(empreinte) == 64
    assert clair != empreinte


def test_generate_reset_token_ne_se_repete_pas():
    assert len({generate_reset_token()[0] for _ in range(50)}) == 50


def test_is_reset_token_expired_distingue_passe_et_futur():
    assert is_reset_token_expired(utc_now_naive() - timedelta(seconds=1)) is True
    assert is_reset_token_expired(utc_now_naive() + timedelta(hours=1)) is False


# ── Purge des sessions (KAN-96) ──────────────────────────────────────────────

def test_purge_supprime_les_sessions_expirees(utilisateur):
    vivante = create_session(utilisateur)
    morte = create_session(utilisateur)
    _perimer(morte)

    assert purge_expired_sessions() == 1

    with SessionLocal() as session:
        restantes = session.execute(select(UserSession)).scalars().all()
    assert [l.refresh_token_hash for l in restantes] == [hash_refresh_token(vivante)]


def test_purge_conserve_une_session_revoquee_non_expiree(utilisateur):
    """
    Point délicat : le critère de purge est l'expiration, **pas** le drapeau
    `revoke`. Une session révoquée par la rotation doit survivre jusqu'au terme
    de son jeton, sinon un jeton volé puis rejoué ne serait plus reconnu comme
    un rejeu — il serait simplement « inconnu », et la détection de vol
    tomberait silencieusement.
    """
    ancien = create_session(utilisateur)
    rotate_refresh_token(ancien)             # l'ancienne session passe à revoke=True

    assert purge_expired_sessions() == 0

    with pytest.raises(ValueError, match="Réutilisation détectée"):
        rotate_refresh_token(ancien)


def test_purge_ciblee_ne_touche_pas_les_autres_comptes(utilisateur, autre_utilisateur):
    mienne = create_session(utilisateur)
    sienne = create_session(autre_utilisateur)
    _perimer(mienne)
    _perimer(sienne)

    assert purge_expired_sessions(utilisateur) == 1

    with SessionLocal() as session:
        restantes = session.execute(select(UserSession)).scalars().all()
    assert [l.user_id for l in restantes] == [autre_utilisateur]


def test_la_connexion_purge_les_sessions_mortes_du_compte(client, utilisateur):
    """
    La table `user_session` s'accumulait indéfiniment : aucune session n'était
    jamais supprimée, ni à expiration ni après révocation. La connexion est le
    moment naturel pour nettoyer, sans tâche planifiée.
    """
    for _ in range(3):
        _perimer(create_session(utilisateur))

    client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": "MotDePasse1"})

    with SessionLocal() as session:
        restantes = session.execute(select(UserSession)).scalars().all()
    assert len(restantes) == 1, "seule la session de la connexion en cours doit subsister"
