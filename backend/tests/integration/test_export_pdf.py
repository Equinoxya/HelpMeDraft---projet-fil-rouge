"""
Tests d'intégration de l'export PDF — GET /documents/<id>/export.pdf.

CE QUI EST EN JEU ICI N'EST PAS LE RENDU mais la garde. Le rendu est vérifié à
part (tests/unit/test_pdf_service.py). Ce fichier vérifie les trois règles que
seul le serveur peut tenir :

  1. on n'exporte que SES documents ;
  2. on n'exporte que les documents TERMINÉS ;
  3. le nom du fichier proposé ne peut pas être détourné par le titre.

La deuxième mérite qu'on insiste : le bouton n'apparaît que sur les documents
terminés, mais l'URL est devinable. Une règle métier laissée à l'interface
n'est pas une règle, c'est une suggestion.
"""

from urllib.parse import quote

import pytest
from sqlalchemy import select

from database.db import Document, SessionLocal


@pytest.fixture
def creer_document(utilisateur):
    """Fabrique de documents : rend l'identifiant du document créé."""

    def _creer(titre="Note de service", content="# Titre\n\nUn paragraphe.", status="termine"):
        with SessionLocal() as session:
            document = Document(
                titre=titre,
                content=content,
                status=status,
                format="markdown",
                user_id=utilisateur,
            )
            session.add(document)
            session.commit()
            return document.id_document

    return _creer


def _export(client, auth, id_document):
    return client.get(f"/documents/{id_document}/export.pdf", headers=auth)


# ── Cas nominal ──────────────────────────────────────────────────────────────


def test_tie20_un_document_termine_s_exporte_en_pdf(client, auth, creer_document):
    reponse = _export(client, auth, creer_document())

    assert reponse.status_code == 200
    assert reponse.mimetype == "application/pdf"
    assert reponse.data.startswith(b"%PDF-")
    assert reponse.data.rstrip().endswith(b"%%EOF")


def test_le_pdf_est_propose_en_telechargement_et_non_affiche(client, auth, creer_document):
    """
    « attachment » et non « inline » : le document est destiné à être conservé
    et transmis, pas consulté dans un onglet — il l'est déjà dans l'éditeur.
    """
    reponse = _export(client, auth, creer_document())

    disposition = reponse.headers["Content-Disposition"]
    assert disposition.startswith("attachment;")
    assert "Note-de-service" in disposition


def test_un_document_termine_sans_contenu_s_exporte_quand_meme(client, auth, creer_document):
    """
    Refuser obligerait l'interface à expliquer un refus incompréhensible : le
    document existe, il est marqué terminé, et l'export échouerait.
    """
    reponse = _export(client, auth, creer_document(content=None))

    assert reponse.status_code == 200
    assert reponse.data.startswith(b"%PDF-")


# ── Règle métier : seuls les documents terminés ──────────────────────────────


@pytest.mark.parametrize("status", ["brouillon", "a_relire"])
def test_tie21_un_document_non_termine_ne_s_exporte_pas(client, auth, creer_document, status):
    """
    LA GARDE EST CÔTÉ SERVEUR. Le bouton n'apparaît que sur les documents
    terminés, mais rien n'empêche d'appeler l'URL directement.

    409 et non 403 : le refus ne tient pas aux droits de l'appelant, qui est
    bien le propriétaire, mais à l'état du document. Changer son statut lève le
    refus, ce qu'un 403 laisserait croire impossible.
    """
    reponse = _export(client, auth, creer_document(status=status))

    assert reponse.status_code == 409
    corps = reponse.get_json()
    assert "terminés" in corps["error"]
    # Le statut courant est renvoyé : l'interface peut dire POURQUOI ça refuse
    # sans avoir à relire le document.
    assert corps["status"] == status


# ── Cloisonnement : on n'exporte que ses documents ───────────────────────────


def test_tie22_le_document_d_un_autre_compte_est_introuvable(client, auth_autre, creer_document):
    """
    RG-01. 404 et non 403 : répondre « interdit » confirmerait l'existence du
    document, donc renseignerait sur les données d'un autre compte. Même choix
    que GET /documents/<id>.
    """
    reponse = _export(client, auth_autre, creer_document())

    assert reponse.status_code == 404
    assert reponse.get_json()["error"] == "Document introuvable"


def test_un_document_inexistant_renvoie_404(client, auth):
    reponse = _export(client, auth, "00000000-0000-0000-0000-000000000000")
    assert reponse.status_code == 404


def test_l_export_exige_une_authentification(client, creer_document):
    reponse = client.get(f"/documents/{creer_document()}/export.pdf")
    assert reponse.status_code == 401


# ── Le titre ne doit pas pouvoir détourner l'en-tête HTTP ────────────────────


@pytest.mark.parametrize(
    "titre",
    [
        "../../etc/passwd",
        'injection" ; attachment; filename="pirate.pdf',
        "retour\nligne",
        "R&D — bilan 2026",
    ],
)
def test_tie23_un_titre_hostile_ne_corrompt_pas_l_en_tete(client, auth, creer_document, titre):
    """
    Le titre est saisi librement et finit dans Content-Disposition. Un retour à
    la ligne y injecterait un en-tête supplémentaire, un guillemet refermerait
    le champ avant terme.
    """
    reponse = _export(client, auth, creer_document(titre=titre))

    assert reponse.status_code == 200
    disposition = reponse.headers["Content-Disposition"]

    assert "\n" not in disposition and "\r" not in disposition
    assert ".." not in disposition
    # Un seul « attachment », donc aucune directive injectée par le titre.
    assert disposition.count("attachment;") == 1


def test_un_titre_accentue_voyage_en_rfc_5987(client, auth, creer_document):
    """
    Le nom simple ne peut porter que de l'ASCII : un titre accentué y arriverait
    tronqué ou en mojibake selon le navigateur. `filename*` porte la version
    UTF-8, que les navigateurs préfèrent lorsqu'elle est présente.
    """
    reponse = _export(client, auth, creer_document(titre="Résumé annuel"))

    disposition = reponse.headers["Content-Disposition"]
    assert "filename*=UTF-8''" in disposition
    assert quote("Résumé") in disposition


# ── Le document n'est pas modifié par son export ─────────────────────────────


def test_l_export_ne_modifie_pas_le_document(client, auth, creer_document):
    """Un GET ne doit rien écrire : ni le statut, ni la date de modification."""
    id_document = creer_document()
    with SessionLocal() as session:
        avant = session.execute(
            select(Document).where(Document.id_document == id_document)
        ).scalar_one()
        statut_avant, modifie_avant = avant.status, avant.updated_at

    assert _export(client, auth, id_document).status_code == 200

    with SessionLocal() as session:
        apres = session.execute(
            select(Document).where(Document.id_document == id_document)
        ).scalar_one()
        assert apres.status == statut_avant
        assert apres.updated_at == modifie_avant
