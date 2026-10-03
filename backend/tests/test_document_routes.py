# -*- coding: utf-8 -*-
"""
Tests d'intégration des routes de documents (§ 9.4).

La suppression était la seule route du projet couverte par aucun test, et c'est
précisément celle qui contenait un défaut : `return "",` au lieu de
`return "", 204` (§ 8.11). Le test ci-dessous aurait suffi à le voir — il est
écrit en premier, et en même temps que le correctif.

Les tests d'accès croisé vérifient la mesure du § 5.7.2 : un document
appartenant à autrui renvoie 404, jamais 403, et la réponse est indiscernable
de celle d'un document inexistant.
"""
from database.db import Document, SessionLocal


def creer_document(client, headers, titre="Compte rendu de réunion"):
    reponse = client.post("/documents", json={"titre": titre}, headers=headers)
    assert reponse.status_code == 201, reponse.get_data(as_text=True)
    return reponse.get_json()["id_document"]


def second_compte(client):
    """Crée et connecte un deuxième compte, pour les tests d'accès croisé."""
    client.post("/auth/register", json={
        "lastname": "Autre", "firstname": "Compte",
        "email": "autre@example.test", "mdp": "MotDePasse1", "rgpd_consent": True,
    })
    reponse = client.post("/auth/login",
                          json={"email": "autre@example.test", "mdp": "MotDePasse1"})
    return {"Authorization": f"Bearer {reponse.get_json()['access_token']}"}


# ── Suppression ──────────────────────────────────────────────────────────────
def test_suppression_renvoie_204_et_retire_la_ligne(client, connecte):
    """LE test qui manquait.

    Il vérifie deux choses distinctes, et c'est volontaire : le code de statut
    ET l'effet en base. Le défaut corrigé supprimait bien la ligne mais échouait
    à construire la réponse — un test qui ne regarderait que la base passerait
    quand même, un test qui ne regarderait que le statut ne prouverait pas la
    suppression.
    """
    id_document = creer_document(client, connecte["headers"])

    reponse = client.delete(f"/documents/{id_document}", headers=connecte["headers"])

    assert reponse.status_code == 204
    assert reponse.get_data() == b""          # 204 : aucun corps
    with SessionLocal() as db:
        assert db.query(Document).filter_by(id_document=id_document).first() is None


def test_supprimer_deux_fois_renvoie_404(client, connecte):
    id_document = creer_document(client, connecte["headers"])
    assert client.delete(f"/documents/{id_document}",
                         headers=connecte["headers"]).status_code == 204
    assert client.delete(f"/documents/{id_document}",
                         headers=connecte["headers"]).status_code == 404


def test_supprimer_le_document_d_autrui_est_indiscernable_d_un_document_absent(
        client, connecte):
    """Anti-énumération (§ 5.7.2) : on compare les corps, pas seulement les codes.

    Et le document de l'autre compte doit SURVIVRE : une réponse 404 qui aurait
    quand même supprimé la ligne serait le pire des deux mondes.
    """
    id_document = creer_document(client, connecte["headers"], "Document de A")
    headers_b = second_compte(client)

    autrui = client.delete(f"/documents/{id_document}", headers=headers_b)
    absent = client.delete("/documents/00000000-0000-4000-8000-000000000000",
                           headers=headers_b)

    assert autrui.status_code == absent.status_code == 404
    assert autrui.get_json() == absent.get_json()
    with SessionLocal() as db:
        assert db.query(Document).filter_by(id_document=id_document).first() is not None


def test_suppression_exige_un_jeton(client, connecte):
    id_document = creer_document(client, connecte["headers"])
    assert client.delete(f"/documents/{id_document}").status_code == 401


# ── Création et lecture, pour que la suppression ne soit pas testée seule ─────
def test_creation_sans_titre_est_refusee(client, connecte):
    reponse = client.post("/documents", json={"content": "du texte"},
                          headers=connecte["headers"])
    assert reponse.status_code == 400


def test_creation_avec_un_statut_hors_liste_est_refusee(client, connecte):
    """Liste blanche sur `status` (§ 8.4) : sûre par construction."""
    reponse = client.post("/documents", json={"titre": "X", "status": "archive"},
                          headers=connecte["headers"])
    assert reponse.status_code == 400


def test_un_document_cree_a_les_valeurs_par_defaut_attendues(client, connecte):
    id_document = creer_document(client, connecte["headers"])
    reponse = client.get(f"/documents/{id_document}", headers=connecte["headers"])
    corps = reponse.get_json()
    assert reponse.status_code == 200
    assert corps["status"] == "brouillon"
    assert corps["format"] == "markdown"


def test_la_liste_ne_montre_que_ses_propres_documents(client, connecte):
    creer_document(client, connecte["headers"], "Document de A")
    headers_b = second_compte(client)
    creer_document(client, headers_b, "Document de B")

    corps = client.get("/documents", headers=headers_b).get_json()
    assert [d["titre"] for d in corps["items"]] == ["Document de B"]
    # `total` doit porter sur le même ensemble que `items`, sinon la pagination
    # annonce un nombre de pages qui ne correspond pas au contenu (§ 7.3.3).
    assert corps["total"] == 1


def test_lire_le_document_d_autrui_renvoie_404(client, connecte):
    id_document = creer_document(client, connecte["headers"])
    headers_b = second_compte(client)
    assert client.get(f"/documents/{id_document}",
                      headers=headers_b).status_code == 404
