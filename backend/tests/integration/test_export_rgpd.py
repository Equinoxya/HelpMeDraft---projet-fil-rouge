"""
Export des données personnelles — RGPD art. 15 (accès) et art. 20 (portabilité).

Deux familles de tests, et la seconde est la plus importante :

  • ce que l'export DOIT contenir — sinon le droit d'accès n'est pas servi ;
  • ce qu'il ne doit SURTOUT pas contenir. Un export est un fichier qui sort de
    l'application et circule par courriel ou clé USB. Y laisser l'empreinte d'un
    mot de passe, un jeton de connexion, les documents d'un autre compte ou
    l'email d'un administrateur transformerait une obligation légale en fuite de
    données.

Les tests d'exclusion cherchent les valeurs RÉELLES dans l'archive décompressée,
et non l'absence d'une clé JSON : c'est la seule façon de prouver qu'une donnée
n'est pas sortie, quel que soit le chemin par lequel elle aurait pu sortir.
"""

import io
import json
import zipfile

import pytest
from sqlalchemy import select

from app.services.export_service import nom_de_fichier_sur
from database.db import SessionLocal, User, UserSession


@pytest.fixture
def auth_admin(client, administrateur, entetes):
    return entetes("admin@exemple.fr")


def _archive(client, auth):
    reponse = client.get("/auth/export", headers=auth)
    assert reponse.status_code == 200, reponse.get_json()
    return reponse, zipfile.ZipFile(io.BytesIO(reponse.data))


def _donnees(archive) -> dict:
    return json.loads(archive.read("donnees.json").decode("utf-8"))


# ── Ce que l'export doit contenir ────────────────────────────────────────────


def test_tie01_l_archive_contient_les_trois_parties(client, auth, utilisateur):
    _, archive = _archive(client, auth)
    noms = archive.namelist()

    assert "donnees.json" in noms
    assert "LISEZ-MOI.txt" in noms


def test_tie02_le_compte_et_ses_donnees_sont_exportes(
    client, auth, utilisateur, creer_document, creer_appels_ia
):
    document = creer_document(utilisateur, titre="Ma lettre", status="brouillon")
    creer_appels_ia(utilisateur, document, nombre=2)

    _, archive = _archive(client, auth)
    donnees = _donnees(archive)

    assert donnees["compte"]["email"] == "camille@exemple.fr"
    assert donnees["compte"]["prenom"] == "Camille"
    assert [doc["titre"] for doc in donnees["documents"]] == ["Ma lettre"]
    assert len(donnees["historique_ia"]) == 2
    assert donnees["export"]["fondement"].startswith("RGPD art. 15")


def test_tie03_chaque_document_a_son_fichier_markdown(client, auth, utilisateur, creer_document):
    creer_document(utilisateur, titre="Ma lettre", status="brouillon")
    creer_document(utilisateur, titre="Note de service", status="termine")

    _, archive = _archive(client, auth)
    fichiers = [nom for nom in archive.namelist() if nom.startswith("documents/")]

    assert len(fichiers) == 2
    assert "documents/01-ma-lettre.md" in fichiers
    assert "documents/02-note-de-service.md" in fichiers


def test_tie04_un_compte_vide_rend_une_archive_valide(client, auth, utilisateur):
    """Structure complète avec des listes vides, et non une erreur."""
    _, archive = _archive(client, auth)
    donnees = _donnees(archive)

    assert donnees["documents"] == []
    assert donnees["dossiers"] == []
    assert donnees["historique_ia"] == []
    assert donnees["compte"]["email"] == "camille@exemple.fr"


def test_tie05_le_nom_du_fichier_propose_vient_de_la_date(client, auth, utilisateur):
    """Et non de l'email : un email dans cet en-tête ouvrirait l'injection d'en-tête."""
    reponse, _ = _archive(client, auth)

    disposition = reponse.headers["Content-Disposition"]
    assert disposition.startswith('attachment; filename="helpmedraft-export-')
    assert disposition.endswith('.zip"')
    assert "camille" not in disposition
    assert reponse.headers["Content-Type"] == "application/zip"


# ── Ce que l'export ne doit SURTOUT pas contenir ─────────────────────────────


def test_tie06_aucune_empreinte_de_mot_de_passe_ne_sort(client, auth, utilisateur):
    """
    On cherche l'empreinte RÉELLE dans l'archive entière, pas l'absence d'une clé.

    C'est la seule façon de prouver qu'elle n'est pas sortie, quel que soit le
    chemin — une sérialisation automatique ajoutée plus tard, par exemple.
    """
    with SessionLocal() as session:
        empreinte = session.execute(
            select(User.mdp_hash).where(User.user_id == utilisateur)
        ).scalar_one()

    reponse, archive = _archive(client, auth)
    brut = reponse.data.decode("latin-1")
    contenu = "".join(archive.read(nom).decode("utf-8") for nom in archive.namelist())

    assert empreinte not in contenu
    assert empreinte not in brut
    assert "mdp_hash" not in contenu


def test_tie07_aucune_empreinte_de_jeton_de_session_ne_sort(client, auth, utilisateur):
    """Les sessions sortent en métadonnées : dates et révocation, rien de rejouable."""
    with SessionLocal() as session:
        empreintes = (
            session.execute(
                select(UserSession.refresh_token_hash).where(UserSession.user_id == utilisateur)
            )
            .scalars()
            .all()
        )
    assert empreintes, "le test n'a de sens que si une session existe"

    _, archive = _archive(client, auth)
    contenu = "".join(archive.read(nom).decode("utf-8") for nom in archive.namelist())
    donnees = _donnees(archive)

    for empreinte in empreintes:
        assert empreinte not in contenu
    assert "refresh_token_hash" not in contenu
    assert donnees["sessions"], "les métadonnées de session doivent bien être exportées"
    assert set(donnees["sessions"][0]) == {"ouverte_le", "expire_le", "revoquee"}


def test_tie08_les_documents_d_un_autre_compte_ne_sortent_pas(
    client, auth, utilisateur, autre_utilisateur, creer_document
):
    """RG-01, appliquée à l'export : le cloisonnement ne souffre aucune exception."""
    creer_document(utilisateur, titre="Le mien", status="brouillon")
    creer_document(autre_utilisateur, titre="SECRET DE DOMINIQUE", status="brouillon")

    _, archive = _archive(client, auth)
    contenu = "".join(archive.read(nom).decode("utf-8") for nom in archive.namelist())

    assert "Le mien" in contenu
    assert "SECRET DE DOMINIQUE" not in contenu
    assert "dominique@exemple.fr" not in contenu


def test_tie09_l_email_de_l_administrateur_ne_sort_pas(
    client, auth, auth_admin, utilisateur, administrateur
):
    """
    Le piège de cet export : l'utilisateur a droit à SES données.

    Les actions d'administration sur son compte lui sont dues, mais l'identité
    de l'administrateur qui les a faites est la donnée d'un TIERS.
    """
    client.patch(f"/admin/users/{utilisateur}", json={"quota_daily_limit": 42}, headers=auth_admin)

    _, archive = _archive(client, auth)
    contenu = "".join(archive.read(nom).decode("utf-8") for nom in archive.namelist())
    donnees = _donnees(archive)

    assert len(donnees["actions_administratives"]) == 1
    assert donnees["actions_administratives"][0]["apres"] == "42"
    assert "admin@exemple.fr" not in contenu, "l'email de l'administrateur a fui"
    assert "acteur_email" not in contenu


def test_tie10_l_export_exige_une_authentification(client, utilisateur):
    assert client.get("/auth/export").status_code == 401


# ── Assainissement des noms de fichiers ─────────────────────────────────────


@pytest.mark.parametrize(
    "titre, attendu",
    [
        ("Ma lettre", "01-ma-lettre.md"),
        # Zip slip : un titre qui remonte dans l'arborescence. Extrait par un
        # outil naïf, il écrirait HORS du dossier de destination.
        ("../../.bashrc", "01-bashrc.md"),
        ("/etc/passwd", "01-etc-passwd.md"),
        ("..\\..\\windows\\system32", "01-windows-system32.md"),
        # Les accents sont transposés, pas supprimés.
        ("Résumé d'activité", "01-resume-d-activite.md"),
        # Nom réservé sous Windows : inouvrable, quelle que soit l'extension.
        ("CON", "01-document.md"),
        # Titre sans aucun caractère retenu : il faut quand même un nom.
        ("...", "01-document.md"),
        ("", "01-document.md"),
    ],
)
def test_tie11_un_titre_ne_peut_pas_sortir_du_dossier(titre, attendu):
    nom = nom_de_fichier_sur(titre, 1)

    assert nom == attendu
    assert "/" not in nom
    assert "\\" not in nom
    assert ".." not in nom


def test_tie12_deux_documents_de_meme_titre_ne_s_ecrasent_pas(
    client, auth, utilisateur, creer_document
):
    creer_document(utilisateur, titre="Lettre", status="brouillon")
    creer_document(utilisateur, titre="Lettre", status="brouillon")

    _, archive = _archive(client, auth)
    fichiers = [nom for nom in archive.namelist() if nom.startswith("documents/")]

    assert len(fichiers) == 2, "le rang en préfixe doit éviter la collision"
    assert len(set(fichiers)) == 2
