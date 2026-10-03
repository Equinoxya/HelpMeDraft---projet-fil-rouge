"""
Tests d'intégration des routes documents et dossiers — TI-20 à TI-30.

Le fil conducteur est RG-01 : un utilisateur n'accède qu'à ses propres
données. Chaque opération est donc testée deux fois — par son propriétaire,
puis par un tiers.
"""

from sqlalchemy import select

from database.db import IA, Consentement, Document, Dossier, SessionLocal, User, UserSession

# ── Création ─────────────────────────────────────────────────────────────────


def test_ti20_creation_rattache_le_document_a_son_auteur(client, auth, utilisateur):
    reponse = client.post("/documents", json={"titre": "Note de service"}, headers=auth)
    assert reponse.status_code == 201
    assert reponse.get_json()["titre"] == "Note de service"

    with SessionLocal() as session:
        document = session.execute(select(Document)).scalar_one()
    assert document.user_id == utilisateur
    assert document.status == "brouillon", "statut par défaut"
    assert document.format == "markdown"


def test_ti21_creation_refuse_un_statut_hors_liste_blanche(client, auth):
    """RG-05 — les statuts sont validés contre un ensemble fermé."""
    reponse = client.post("/documents", json={"titre": "Note", "status": "archive"}, headers=auth)
    assert reponse.status_code == 400


def test_creation_refuse_un_format_hors_liste_blanche(client, auth):
    reponse = client.post("/documents", json={"titre": "Note", "format": "pdf"}, headers=auth)
    assert reponse.status_code == 400


def test_creation_refuse_un_titre_vide_ou_absent(client, auth):
    assert client.post("/documents", json={}, headers=auth).status_code == 400
    assert client.post("/documents", json={"titre": "   "}, headers=auth).status_code == 400


def test_creation_refuse_un_titre_trop_long(client, auth):
    reponse = client.post("/documents", json={"titre": "x" * 256}, headers=auth)
    assert reponse.status_code == 400


def test_creation_accepte_un_titre_a_la_borne(client, auth):
    """La borne de 255 caractères doit être inclusive."""
    reponse = client.post("/documents", json={"titre": "x" * 255}, headers=auth)
    assert reponse.status_code == 201


def test_creation_refuse_un_dossier_appartenant_a_autrui(
    client, auth, autre_utilisateur, creer_dossier
):
    dossier_tiers = creer_dossier(autre_utilisateur)
    reponse = client.post(
        "/documents", json={"titre": "Note", "id_dossier": dossier_tiers}, headers=auth
    )
    assert reponse.status_code == 404


# ── Lecture et cloisonnement ─────────────────────────────────────────────────


def test_ti22_chacun_ne_voit_que_ses_documents(
    client, auth, auth_autre, utilisateur, autre_utilisateur, creer_document
):
    creer_document(utilisateur, titre="Le mien")
    creer_document(autre_utilisateur, titre="Le sien")

    mes_documents = client.get("/documents", headers=auth).get_json()
    ses_documents = client.get("/documents", headers=auth_autre).get_json()

    assert [d["titre"] for d in mes_documents["items"]] == ["Le mien"]
    assert [d["titre"] for d in ses_documents["items"]] == ["Le sien"]
    assert mes_documents["total"] == ses_documents["total"] == 1


def test_ti23_lire_le_document_d_autrui_rend_404_et_non_403(
    client, auth, autre_utilisateur, creer_document
):
    """
    Un 403 confirmerait à un attaquant que l'identifiant existe. La requête
    filtre sur (id_document, user_id) conjointement : du point de vue de
    l'appelant, le document n'existe tout simplement pas.
    """
    document_tiers = creer_document(autre_utilisateur)
    reponse = client.get(f"/documents/{document_tiers}", headers=auth)
    assert reponse.status_code == 404


def test_lecture_d_un_identifiant_inexistant_rend_404(client, auth):
    assert client.get("/documents/identifiant-invente", headers=auth).status_code == 404


def test_les_routes_documents_exigent_une_authentification(client):
    assert client.get("/documents").status_code == 401
    assert client.post("/documents", json={"titre": "x"}).status_code == 401


def test_pagination_refuse_des_bornes_invalides(client, auth):
    assert client.get("/documents?page=0", headers=auth).status_code == 400
    assert client.get("/documents?per_page=51", headers=auth).status_code == 400
    assert client.get("/documents?page=abc", headers=auth).status_code == 400


# ── Modification ─────────────────────────────────────────────────────────────


def test_modification_par_le_proprietaire(client, auth, utilisateur, creer_document):
    document = creer_document(utilisateur)
    reponse = client.put(
        f"/documents/{document}", json={"content": "Nouveau contenu."}, headers=auth
    )
    assert reponse.status_code == 200
    assert reponse.get_json()["content"] == "Nouveau contenu."


def test_ti24_modifier_le_document_d_autrui_ne_change_rien(
    client, auth, autre_utilisateur, creer_document
):
    document_tiers = creer_document(autre_utilisateur, contenu="Contenu d'origine.")

    reponse = client.put(
        f"/documents/{document_tiers}", json={"content": "Détourné."}, headers=auth
    )
    assert reponse.status_code == 404

    with SessionLocal() as session:
        inchange = session.get(Document, document_tiers)
    assert inchange.content == "Contenu d'origine.", "le contenu ne doit pas avoir bougé"


def test_modification_partielle_ne_touche_pas_les_autres_champs(
    client, auth, utilisateur, creer_document
):
    document = creer_document(utilisateur, titre="Titre initial", contenu="Contenu initial.")
    client.put(f"/documents/{document}", json={"status": "termine"}, headers=auth)

    with SessionLocal() as session:
        apres = session.get(Document, document)
    assert apres.titre == "Titre initial"
    assert apres.content == "Contenu initial."
    assert apres.status == "termine"


# ── Suppression ──────────────────────────────────────────────────────────────


def test_ti25_suppression_par_le_proprietaire(client, auth, utilisateur, creer_document):
    """
    Régression KAN-93 : la route renvoyait `return "",` — un tuple à un seul
    élément, que Flask refuse, ce qui produisait une erreur 500 au lieu d'un
    204. Ce test échoue si la régression revient.
    """
    document = creer_document(utilisateur)
    reponse = client.delete(f"/documents/{document}", headers=auth)

    assert reponse.status_code == 204
    with SessionLocal() as session:
        assert session.get(Document, document) is None


def test_ti26_supprimer_le_document_d_autrui_ne_supprime_rien(
    client, auth, autre_utilisateur, creer_document
):
    document_tiers = creer_document(autre_utilisateur)

    assert client.delete(f"/documents/{document_tiers}", headers=auth).status_code == 404
    with SessionLocal() as session:
        assert session.get(Document, document_tiers) is not None


# ── Statistiques ─────────────────────────────────────────────────────────────


def test_ti30_les_statistiques_comptent_par_statut(client, auth, utilisateur, creer_document):
    creer_document(utilisateur, titre="A", status="brouillon")
    creer_document(utilisateur, titre="B", status="brouillon")
    creer_document(utilisateur, titre="C", status="termine")

    corps = client.get("/documents/stats", headers=auth).get_json()
    assert corps == {"total": 3, "brouillon": 2, "a_relire": 0, "termine": 1}


def test_les_statistiques_ignorent_les_documents_d_autrui(
    client, auth, utilisateur, autre_utilisateur, creer_document
):
    creer_document(utilisateur, titre="Le mien")
    creer_document(autre_utilisateur, titre="Le sien")

    assert client.get("/documents/stats", headers=auth).get_json()["total"] == 1


# ── Dossiers ─────────────────────────────────────────────────────────────────


def test_ti27_creation_de_dossier(client, auth, utilisateur):
    reponse = client.post("/dossiers", json={"name": "Contrats"}, headers=auth)
    assert reponse.status_code == 201
    assert reponse.get_json()["document_count"] == 0


def test_creation_de_dossier_refuse_un_nom_vide(client, auth):
    assert client.post("/dossiers", json={"name": "  "}, headers=auth).status_code == 400
    assert client.post("/dossiers", json={}, headers=auth).status_code == 400


def test_la_liste_des_dossiers_compte_les_documents(
    client, auth, utilisateur, creer_dossier, creer_document
):
    dossier = creer_dossier(utilisateur)
    creer_document(utilisateur, titre="A", id_dossier=dossier)
    creer_document(utilisateur, titre="B", id_dossier=dossier)
    creer_document(utilisateur, titre="Hors dossier")

    dossiers = client.get("/dossiers", headers=auth).get_json()
    assert len(dossiers) == 1
    assert dossiers[0]["document_count"] == 2


def test_ti28_supprimer_un_dossier_declasse_ses_documents_sans_les_detruire(
    client, auth, utilisateur, creer_dossier, creer_document
):
    """
    RG-03 — supprimer un classement ne doit jamais détruire le travail.
    Le ON DELETE SET NULL remet id_dossier à NULL ; les documents restent.
    """
    dossier = creer_dossier(utilisateur)
    document_a = creer_document(utilisateur, titre="A", id_dossier=dossier)
    document_b = creer_document(utilisateur, titre="B", id_dossier=dossier)

    assert client.delete(f"/dossiers/{dossier}", headers=auth).status_code == 204

    with SessionLocal() as session:
        for identifiant in (document_a, document_b):
            document = session.get(Document, identifiant)
            assert document is not None, "le document ne doit pas être supprimé"
            assert document.id_dossier is None, "il doit être déclassé"


def test_supprimer_le_dossier_d_autrui_rend_404(client, auth, autre_utilisateur, creer_dossier):
    dossier_tiers = creer_dossier(autre_utilisateur)
    assert client.delete(f"/dossiers/{dossier_tiers}", headers=auth).status_code == 404


# ── Intégrité référentielle ──────────────────────────────────────────────────


def test_ti29_supprimer_un_compte_efface_toutes_ses_donnees(
    client, utilisateur, creer_dossier, creer_document, creer_appels_ia
):
    """
    RG-04 — droit à l'effacement (RGPD art. 17). Aucune donnée orpheline ne
    doit subsister après la suppression du compte.
    """
    dossier = creer_dossier(utilisateur)
    document = creer_document(utilisateur, id_dossier=dossier)
    creer_appels_ia(utilisateur, document, nombre=3)
    client.post("/auth/login", json={"email": "camille@exemple.fr", "mdp": "MotDePasse1"})

    with SessionLocal() as session:
        session.delete(session.get(User, utilisateur))
        session.commit()

    with SessionLocal() as session:
        for modele in (Document, Dossier, IA, Consentement, UserSession):
            restants = session.execute(select(modele)).scalars().all()
            assert restants == [], f"{modele.__name__} : {len(restants)} ligne(s) orpheline(s)"
