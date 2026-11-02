"""
Journal des actions d'administration, recherche de comptes, et confirmation de
suppression.

Ce qui est vérifié ici tient en une phrase : le back-office touche aux droits et
détruit des données, donc chaque action doit laisser une trace qui SURVIT à son
objet, et une suppression ne doit pas pouvoir partir sur un identifiant pris au
hasard.

Les cas de survie (TI-J04, TI-J05) sont les plus importants : ce sont eux qui
justifient la dénormalisation des emails et l'absence de clé étrangère vers la
cible. Les écrire autrement — avec des clés étrangères en cascade — ferait
disparaître la trace au moment même où elle devient utile.
"""

from datetime import timedelta

import pytest
from sqlalchemy import select

from app.services.journal_service import RETENTION_JOURS, purge_journal_admin
from database.db import JournalAdmin, SessionLocal, User
from utilitaires import utc_now_naive


@pytest.fixture
def auth_admin(client, administrateur, entetes):
    return entetes("admin@exemple.fr")


def _journal() -> list[JournalAdmin]:
    with SessionLocal() as session:
        return list(
            session.execute(select(JournalAdmin).order_by(JournalAdmin.created_at.asc())).scalars()
        )


# ── Écriture du journal ──────────────────────────────────────────────────────


def test_tij01_un_changement_de_role_est_trace(client, auth_admin, utilisateur):
    reponse = client.patch(
        f"/admin/users/{utilisateur}", json={"role": "admin"}, headers=auth_admin
    )
    assert reponse.status_code == 200

    lignes = _journal()
    assert len(lignes) == 1
    assert lignes[0].action == "role"
    assert lignes[0].acteur_email == "admin@exemple.fr"
    assert lignes[0].cible_email == "camille@exemple.fr"
    assert (lignes[0].avant, lignes[0].apres) == ("user", "admin")


def test_tij02_un_changement_de_quota_est_trace(client, auth_admin, utilisateur):
    client.patch(f"/admin/users/{utilisateur}", json={"quota_daily_limit": 50}, headers=auth_admin)

    lignes = _journal()
    assert len(lignes) == 1
    assert lignes[0].action == "quota"
    assert (lignes[0].avant, lignes[0].apres) == ("20", "50")


def test_tij03_reecrire_la_meme_valeur_ne_trace_rien(client, auth_admin, utilisateur):
    """Réécrire une valeur à l'identique n'est pas une action d'administration."""
    reponse = client.patch(
        f"/admin/users/{utilisateur}",
        json={"role": "user", "quota_daily_limit": 20},
        headers=auth_admin,
    )

    assert reponse.status_code == 200
    assert _journal() == []


def test_tij04_la_trace_survit_a_la_suppression_de_la_cible(client, auth_admin, utilisateur):
    """
    LE cas qui justifie la conception de la table.

    La cible n'existe plus, et c'est justement l'action qu'il faut pouvoir
    relire. Avec une clé étrangère vers `user`, la ligne serait partie en
    cascade ou aurait bloqué la suppression.
    """
    client.delete(f"/admin/users/{utilisateur}?confirmation=camille@exemple.fr", headers=auth_admin)

    with SessionLocal() as session:
        assert session.get(User, utilisateur) is None

    lignes = _journal()
    assert len(lignes) == 1
    assert lignes[0].action == "suppression"
    assert lignes[0].cible_email == "camille@exemple.fr", "l'identité de la cible est perdue"
    assert lignes[0].cible_id == utilisateur


def test_tij05_la_trace_survit_a_la_suppression_de_l_acteur(
    client, auth_admin, administrateur, creer_utilisateur, entetes
):
    """
    Supprimer un administrateur ne doit pas effacer ce qu'il a fait.

    `acteur_id` passe à NULL (ON DELETE SET NULL), mais `acteur_email` reste :
    on sait encore QUI a agi.
    """
    second_admin = creer_utilisateur("second.admin@exemple.fr", role="admin")
    cible = creer_utilisateur("cible@exemple.fr")

    # Le second administrateur agit, puis le premier le supprime.
    client.patch(
        f"/admin/users/{cible}", json={"role": "admin"}, headers=entetes("second.admin@exemple.fr")
    )
    client.delete(
        f"/admin/users/{second_admin}?confirmation=second.admin@exemple.fr", headers=auth_admin
    )

    lignes = [ligne for ligne in _journal() if ligne.action == "role"]
    assert len(lignes) == 1
    assert lignes[0].acteur_id is None, "la clé étrangère doit passer à NULL, pas effacer la ligne"
    assert lignes[0].acteur_email == "second.admin@exemple.fr"


# ── Confirmation de suppression ──────────────────────────────────────────────


def test_tij06_une_suppression_sans_confirmation_est_refusee(client, auth_admin, utilisateur):
    reponse = client.delete(f"/admin/users/{utilisateur}", headers=auth_admin)

    assert reponse.status_code == 400
    # Le message doit dire que le PARAMÈTRE manque, et non que la confirmation
    # ne correspond pas : sans cette distinction, le test passerait encore si le
    # contrôle d'absence disparaissait, la comparaison d'email renvoyant elle
    # aussi un 400. Vérifié par mutation.
    assert "exige le paramètre" in reponse.get_json()["error"]
    with SessionLocal() as session:
        assert session.get(User, utilisateur) is not None
    assert _journal() == [], "une suppression refusée ne doit rien tracer"


def test_tij07_une_confirmation_qui_ne_correspond_pas_est_refusee(
    client, auth_admin, utilisateur, autre_utilisateur
):
    """Le cas réel : l'identifiant d'un compte, l'email d'un autre."""
    reponse = client.delete(
        f"/admin/users/{utilisateur}?confirmation=dominique@exemple.fr", headers=auth_admin
    )

    assert reponse.status_code == 400
    with SessionLocal() as session:
        assert session.get(User, utilisateur) is not None
        assert session.get(User, autre_utilisateur) is not None


def test_tij08_la_confirmation_ignore_la_casse(client, auth_admin, utilisateur):
    """Exiger la casse exacte ferait échouer une confirmation pourtant juste."""
    reponse = client.delete(
        f"/admin/users/{utilisateur}?confirmation=Camille@Exemple.FR", headers=auth_admin
    )

    assert reponse.status_code == 204


# ── Lecture du journal ───────────────────────────────────────────────────────


def test_tij09_le_journal_se_lit_du_plus_recent_au_plus_ancien(
    client, auth_admin, utilisateur, autre_utilisateur
):
    client.patch(f"/admin/users/{utilisateur}", json={"role": "admin"}, headers=auth_admin)
    client.patch(
        f"/admin/users/{autre_utilisateur}", json={"quota_daily_limit": 7}, headers=auth_admin
    )

    corps = client.get("/admin/journal", headers=auth_admin).get_json()

    assert corps["total"] == 2
    assert [item["action"] for item in corps["items"]] == ["quota", "role"]
    assert corps["retention_jours"] == RETENTION_JOURS


def test_tij10_le_journal_se_filtre_par_action(client, auth_admin, utilisateur, autre_utilisateur):
    client.patch(f"/admin/users/{utilisateur}", json={"role": "admin"}, headers=auth_admin)
    client.patch(
        f"/admin/users/{autre_utilisateur}", json={"quota_daily_limit": 7}, headers=auth_admin
    )

    corps = client.get("/admin/journal?action=role", headers=auth_admin).get_json()

    assert corps["total"] == 1, "le total doit compter les lignes FILTRÉES"
    assert corps["items"][0]["action"] == "role"


def test_tij11_une_action_hors_liste_est_refusee(client, auth_admin):
    reponse = client.get("/admin/journal?action=tout_effacer", headers=auth_admin)

    assert reponse.status_code == 400


def test_tij12_un_utilisateur_standard_ne_lit_pas_le_journal(client, auth, utilisateur):
    assert client.get("/admin/journal", headers=auth).status_code == 403


def test_tij13_aucune_route_ne_permet_d_ecrire_ou_de_supprimer_le_journal(client, auth_admin):
    """
    Un journal que l'administrateur peut retoucher ne prouve rien.

    Les écritures ne viennent que des routes d'administration, dans la
    transaction de l'action tracée, et la seule suppression est la purge de
    rétention.
    """
    for methode in (client.post, client.patch, client.put, client.delete):
        assert methode("/admin/journal", headers=auth_admin).status_code == 405


# ── Rétention ────────────────────────────────────────────────────────────────


def test_tij14_la_purge_retire_les_entrees_hors_retention(client, auth_admin, utilisateur):
    client.patch(f"/admin/users/{utilisateur}", json={"role": "admin"}, headers=auth_admin)

    # On vieillit artificiellement la ligne au-delà de la rétention.
    with SessionLocal() as session:
        ligne = session.execute(select(JournalAdmin)).scalars().one()
        ligne.created_at = utc_now_naive() - timedelta(days=RETENTION_JOURS + 1)
        session.commit()

    assert purge_journal_admin() == 1
    assert _journal() == []


def test_tij15_la_purge_epargne_les_entrees_dans_la_retention(client, auth_admin, utilisateur):
    client.patch(f"/admin/users/{utilisateur}", json={"role": "admin"}, headers=auth_admin)

    with SessionLocal() as session:
        ligne = session.execute(select(JournalAdmin)).scalars().one()
        ligne.created_at = utc_now_naive() - timedelta(days=RETENTION_JOURS - 1)
        session.commit()

    assert purge_journal_admin() == 0
    assert len(_journal()) == 1


# ── Recherche dans la liste des comptes ──────────────────────────────────────


def test_tij16_la_recherche_filtre_sur_l_email(client, auth_admin, utilisateur, autre_utilisateur):
    corps = client.get("/admin/users?recherche=dominique", headers=auth_admin).get_json()

    assert corps["total"] == 1, "le total doit compter les comptes FILTRÉS"
    assert [item["email"] for item in corps["items"]] == ["dominique@exemple.fr"]
    assert corps["recherche"] == "dominique"


def test_tij17_la_recherche_ignore_la_casse_et_porte_aussi_sur_le_nom(
    client, auth_admin, utilisateur
):
    corps = client.get("/admin/users?recherche=DUPONT", headers=auth_admin).get_json()

    assert corps["total"] >= 1
    assert any(item["lastname"] == "Dupont" for item in corps["items"])


def test_tij18_une_recherche_sans_resultat_rend_une_liste_vide(client, auth_admin, utilisateur):
    corps = client.get("/admin/users?recherche=introuvable", headers=auth_admin).get_json()

    assert corps["total"] == 0
    assert corps["items"] == []


def test_tij19_une_recherche_trop_longue_est_refusee(client, auth_admin, utilisateur):
    """Les jokers d'ilike sont inoffensifs, mais un motif à rallonge coûte cher."""
    reponse = client.get(f"/admin/users?recherche={'a' * 129}", headers=auth_admin)

    assert reponse.status_code == 400


def test_tij20_un_joker_sql_est_traite_comme_du_texte(
    client, auth_admin, utilisateur, autre_utilisateur
):
    """
    « % » ne doit pas se comporter comme un joker venu du client.

    Il est passé en paramètre lié par l'ORM : la recherche porte sur le
    caractère lui-même, qu'aucun des deux emails ne contient.
    """
    corps = client.get("/admin/users?recherche=%25", headers=auth_admin).get_json()

    assert corps["total"] == 0, "un joker fourni par le client ne doit pas tout ramener"
