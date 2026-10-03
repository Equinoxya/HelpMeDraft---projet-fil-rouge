"""
Tests d'intégration du back-office — TI-60 à TI-65.

L'enjeu principal est l'autorisation : le garde de navigation côté client est
un confort d'interface, entièrement contournable. La seule barrière réelle est
`require_admin`, vérifié ici.
"""

from database.db import SessionLocal, User

# ── Autorisation ─────────────────────────────────────────────────────────────


def test_ti60_un_utilisateur_standard_est_refuse_sur_tout_le_back_office(
    client, auth, administrateur
):
    assert client.get("/admin/users", headers=auth).status_code == 403
    assert client.get("/admin/stats", headers=auth).status_code == 403
    assert (
        client.patch(
            f"/admin/users/{administrateur}", json={"role": "user"}, headers=auth
        ).status_code
        == 403
    )
    assert client.delete(f"/admin/users/{administrateur}", headers=auth).status_code == 403


def test_le_back_office_exige_une_authentification(client):
    assert client.get("/admin/users").status_code == 401
    assert client.get("/admin/stats").status_code == 401


# ── Liste des comptes ────────────────────────────────────────────────────────


def test_ti61_l_administrateur_liste_les_comptes_avec_leurs_compteurs(
    client, auth_admin, utilisateur, creer_document, creer_appels_ia
):
    document = creer_document(utilisateur)
    creer_appels_ia(utilisateur, document, nombre=3)

    corps = client.get("/admin/users", headers=auth_admin).get_json()
    comptes = {c["email"]: c for c in corps["items"]}

    assert comptes["camille@exemple.fr"]["nb_documents"] == 1
    assert comptes["camille@exemple.fr"]["nb_appels_ia"] == 3
    assert "mdp_hash" not in comptes["camille@exemple.fr"], (
        "l'empreinte du mot de passe ne doit jamais sortir, même pour un administrateur"
    )


# ── Modification d'un compte ─────────────────────────────────────────────────


def test_l_administrateur_modifie_un_role(client, auth_admin, utilisateur):
    reponse = client.patch(
        f"/admin/users/{utilisateur}", json={"role": "admin"}, headers=auth_admin
    )
    assert reponse.status_code == 200

    with SessionLocal() as session:
        assert session.get(User, utilisateur).role == "admin"


def test_ti62_un_role_hors_liste_blanche_est_refuse(client, auth_admin, utilisateur):
    reponse = client.patch(
        f"/admin/users/{utilisateur}", json={"role": "superadmin"}, headers=auth_admin
    )
    assert reponse.status_code == 400


def test_ti63_un_quota_hors_bornes_est_refuse(client, auth_admin, utilisateur):
    for quota in (0, -5, 1001):
        reponse = client.patch(
            f"/admin/users/{utilisateur}",
            json={"quota_daily_limit": quota},
            headers=auth_admin,
        )
        assert reponse.status_code == 400, f"quota={quota}"


def test_un_quota_booleen_est_refuse(client, auth_admin, utilisateur):
    """
    En Python, bool hérite de int : sans exclusion explicite, True passerait
    la validation `isinstance(quota, int)` et vaudrait un quota de 1.
    """
    reponse = client.patch(
        f"/admin/users/{utilisateur}", json={"quota_daily_limit": True}, headers=auth_admin
    )
    assert reponse.status_code == 400


def test_une_modification_sans_champ_valide_est_refusee(client, auth_admin, utilisateur):
    reponse = client.patch(
        f"/admin/users/{utilisateur}", json={"email": "x@y.fr"}, headers=auth_admin
    )
    assert reponse.status_code == 400


def test_un_administrateur_ne_peut_pas_se_retirer_ses_droits(client, auth_admin, administrateur):
    """Garde-fou : sinon le dernier administrateur peut se verrouiller dehors."""
    reponse = client.patch(
        f"/admin/users/{administrateur}", json={"role": "user"}, headers=auth_admin
    )
    assert reponse.status_code == 400

    with SessionLocal() as session:
        assert session.get(User, administrateur).role == "admin"


def test_modifier_un_compte_inexistant_rend_404(client, auth_admin):
    reponse = client.patch(
        "/admin/users/identifiant-invente", json={"role": "user"}, headers=auth_admin
    )
    assert reponse.status_code == 404


# ── Suppression d'un compte ──────────────────────────────────────────────────


def test_l_administrateur_supprime_un_compte(client, auth_admin, utilisateur):
    assert client.delete(f"/admin/users/{utilisateur}", headers=auth_admin).status_code == 204
    with SessionLocal() as session:
        assert session.get(User, utilisateur) is None


def test_ti64_un_administrateur_ne_peut_pas_se_supprimer(client, auth_admin, administrateur):
    assert client.delete(f"/admin/users/{administrateur}", headers=auth_admin).status_code == 400
    with SessionLocal() as session:
        assert session.get(User, administrateur) is not None


# ── Statistiques globales ────────────────────────────────────────────────────


def test_ti65_les_statistiques_globales_sont_coherentes(
    client, auth_admin, utilisateur, administrateur, creer_document, creer_appels_ia
):
    document = creer_document(utilisateur, titre="A", status="brouillon")
    creer_document(utilisateur, titre="B", status="termine")
    creer_appels_ia(utilisateur, document, nombre=2, heures_avant=1)
    creer_appels_ia(utilisateur, document, nombre=1, heures_avant=48)

    corps = client.get("/admin/stats", headers=auth_admin).get_json()

    assert corps["total_users"] == 2
    assert corps["total_documents"] == 2
    assert corps["total_ia_calls_today"] == 2, "la fenêtre de 24 h exclut l'appel de 48 h"
    assert corps["total_ia_calls_7j"] == 3
    assert corps["documents_by_status"] == {"brouillon": 1, "a_relire": 0, "termine": 1}
