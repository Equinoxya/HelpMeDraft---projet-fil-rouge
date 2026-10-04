"""
Tests d'intégration du marquage d'insertion — TI-60 à TI-69.

La table `ia` atteste depuis toujours qu'une proposition a été PRODUITE. Ces
tests portent sur la colonne qui dit qu'elle a été ACCEPTÉE : c'est elle qui
constitue la trace exigée par l'article 50 du règlement UE 2024/1689, et sans
elle une proposition rejetée et une proposition versée au document sont
indiscernables en base.

Trois propriétés sont vérifiées en plus du cas nominal, parce qu'aucune n'est
visible depuis l'interface :
  — le cloisonnement (TI-63 à TI-65), avec des réponses indiscernables ;
  — l'idempotence (TI-66), qui doit préserver l'horodatage d'origine ;
  — la validation de position_debut (TI-67, TI-68), y compris le piège du
    booléen, que Python fait passer pour un entier.
"""

from sqlalchemy import select

from database.db import IA, SessionLocal

CONTENU = "bonjour je voulais savoir si vous aviez recu mon dossier"


def _generer(client, auth, document, ollama_double, retour=("Texte reformulé.", 42)):
    """Produit une interaction IA et renvoie son identifiant."""
    ollama_double(retour=retour)
    reponse = client.post(
        f"/documents/{document}/ia/generer",
        json={"type_action": "reformuler", "scope": "selection", "contenu": CONTENU},
        headers=auth,
    )
    assert reponse.status_code == 201
    return reponse.get_json()["id_ia"]


def _ligne(id_ia):
    with SessionLocal() as session:
        return session.execute(select(IA).where(IA.id_ia == id_ia)).scalar_one()


# ── Cas nominal ──────────────────────────────────────────────────────────────


def test_ti60_marquer_une_insertion_pose_la_trace(
    client, auth, utilisateur, creer_document, ollama_double
):
    document = creer_document(utilisateur)
    id_ia = _generer(client, auth, document, ollama_double)

    reponse = client.post(
        f"/documents/{document}/ia/{id_ia}/insertion",
        json={"position_debut": 12},
        headers=auth,
    )

    assert reponse.status_code == 200
    corps = reponse.get_json()
    assert corps["insere"] is True
    assert corps["position_debut"] == 12
    assert corps["insere_at"]

    ligne = _ligne(id_ia)
    assert ligne.insere is True
    assert ligne.position_debut == 12
    assert ligne.insere_at is not None


def test_ti61_une_generation_non_marquee_reste_non_inseree(
    client, auth, utilisateur, creer_document, ollama_double
):
    """
    La distinction qui porte toute la valeur de la trace : générer n'est pas
    accepter. Sans ce test, une implémentation qui marquerait l'insertion dès
    la génération passerait tous les autres.
    """
    document = creer_document(utilisateur)
    id_ia = _generer(client, auth, document, ollama_double)

    ligne = _ligne(id_ia)
    assert ligne.insere is False
    assert ligne.position_debut is None
    assert ligne.insere_at is None


def test_ti62_l_historique_expose_l_etat_d_insertion(
    client, auth, utilisateur, creer_document, ollama_double
):
    document = creer_document(utilisateur)
    id_insere = _generer(client, auth, document, ollama_double, retour=("Accepté.", 10))
    id_rejete = _generer(client, auth, document, ollama_double, retour=("Rejeté.", 10))

    client.post(
        f"/documents/{document}/ia/{id_insere}/insertion",
        json={"position_debut": 0},
        headers=auth,
    )

    historique = client.get(f"/documents/{document}/ia/historique", headers=auth).get_json()
    par_id = {entree["id_ia"]: entree for entree in historique}

    assert par_id[id_insere]["insere"] is True
    assert par_id[id_insere]["insere_at"]
    assert par_id[id_rejete]["insere"] is False
    assert par_id[id_rejete]["insere_at"] is None


# ── Cloisonnement ────────────────────────────────────────────────────────────


def test_ti63_marquer_l_interaction_d_un_tiers_est_refuse(
    client, auth, auth_autre, utilisateur, autre_utilisateur, creer_document, ollama_double
):
    document_tiers = creer_document(autre_utilisateur)
    id_ia = _generer(client, auth_autre, document_tiers, ollama_double)

    reponse = client.post(
        f"/documents/{document_tiers}/ia/{id_ia}/insertion",
        json={"position_debut": 0},
        headers=auth,
    )

    assert reponse.status_code == 404
    assert _ligne(id_ia).insere is False


def test_ti64_interaction_d_un_tiers_indiscernable_d_une_interaction_absente(
    client, auth, auth_autre, utilisateur, autre_utilisateur, creer_document, ollama_double
):
    """
    Le résultat attendu n'est pas « 404 dans les deux cas » mais LA MÊME
    réponse dans les deux cas. Deux 404 porteurs de messages différents
    rétabliraient la fuite d'information que le 404 sert à fermer.
    """
    document_tiers = creer_document(autre_utilisateur)
    id_ia = _generer(client, auth_autre, document_tiers, ollama_double)

    existante = client.post(
        f"/documents/{document_tiers}/ia/{id_ia}/insertion",
        json={"position_debut": 0},
        headers=auth,
    )
    inexistante = client.post(
        f"/documents/{document_tiers}/ia/00000000-0000-4000-8000-000000000000/insertion",
        json={"position_debut": 0},
        headers=auth,
    )

    assert existante.status_code == inexistante.status_code == 404
    assert existante.get_json() == inexistante.get_json()


def test_ti65_interaction_rattachee_a_un_autre_document_du_meme_compte(
    client, auth, utilisateur, creer_document, ollama_double
):
    """
    Le cloisonnement ne tient pas qu'entre comptes. L'interaction doit aussi
    appartenir AU DOCUMENT cité dans l'URL, sinon la trace se poserait sur un
    document qui n'a jamais reçu ce texte.
    """
    document_a = creer_document(utilisateur, titre="A")
    document_b = creer_document(utilisateur, titre="B")
    id_ia = _generer(client, auth, document_a, ollama_double)

    reponse = client.post(
        f"/documents/{document_b}/ia/{id_ia}/insertion",
        json={"position_debut": 0},
        headers=auth,
    )

    assert reponse.status_code == 404
    assert _ligne(id_ia).insere is False


def test_ti66_sans_authentification(client, utilisateur, creer_document):
    document = creer_document(utilisateur)
    reponse = client.post(
        f"/documents/{document}/ia/00000000-0000-4000-8000-000000000000/insertion",
        json={"position_debut": 0},
    )
    assert reponse.status_code == 401


# ── Idempotence ──────────────────────────────────────────────────────────────


def test_ti67_marquer_deux_fois_preserve_l_horodatage_d_origine(
    client, auth, utilisateur, creer_document, ollama_double
):
    """
    Un double clic, un rejeu de requête ou une reprise après coupure réseau ne
    doivent ni produire d'erreur ni réécrire l'horodatage — qui est précisément
    la donnée que la trace conserve.
    """
    document = creer_document(utilisateur)
    id_ia = _generer(client, auth, document, ollama_double)

    premier = client.post(
        f"/documents/{document}/ia/{id_ia}/insertion",
        json={"position_debut": 7},
        headers=auth,
    )
    second = client.post(
        f"/documents/{document}/ia/{id_ia}/insertion",
        json={"position_debut": 999},
        headers=auth,
    )

    assert premier.status_code == second.status_code == 200
    assert second.get_json()["insere_at"] == premier.get_json()["insere_at"]
    # La seconde position est ignorée : la trace porte sur la PREMIÈRE
    # insertion, les suivantes sont le même événement rejoué.
    assert _ligne(id_ia).position_debut == 7


# ── Validation de l'entrée ───────────────────────────────────────────────────


def test_ti68_position_debut_absente_ou_mal_typee(
    client, auth, utilisateur, creer_document, ollama_double
):
    document = creer_document(utilisateur)
    id_ia = _generer(client, auth, document, ollama_double)
    url = f"/documents/{document}/ia/{id_ia}/insertion"

    for charge in ({}, {"position_debut": "12"}, {"position_debut": -1}, {"position_debut": 1.5}):
        reponse = client.post(url, json=charge, headers=auth)
        assert reponse.status_code == 400, charge

    assert _ligne(id_ia).insere is False


def test_ti69_position_debut_booleenne_est_refusee(
    client, auth, utilisateur, creer_document, ollama_double
):
    """
    En Python, isinstance(True, int) vaut True : sans exclusion explicite du
    booléen, {"position_debut": true} passerait la validation et serait
    enregistré comme un décalage de 1. Le même piège a déjà été rencontré sur
    quota_daily_limit (§ 8.4 du dossier) — un test le verrouille désormais ici.
    """
    document = creer_document(utilisateur)
    id_ia = _generer(client, auth, document, ollama_double)

    reponse = client.post(
        f"/documents/{document}/ia/{id_ia}/insertion",
        json={"position_debut": True},
        headers=auth,
    )

    assert reponse.status_code == 400
    assert _ligne(id_ia).insere is False
