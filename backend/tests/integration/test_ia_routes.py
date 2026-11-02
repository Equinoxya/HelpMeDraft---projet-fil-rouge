"""
Tests d'intégration de la route d'inférence — TI-40 à TI-53.

Fonctionnalité la plus représentative du projet : elle traverse les quatre
couches et mobilise authentification, validation, autorisation, règle de
gestion (quota), service externe et écriture d'une trace.

Le service d'inférence est systématiquement remplacé par un double : la
qualité du texte produit n'est pas testable, la mécanique autour l'est.
"""

from sqlalchemy import select

from database.db import IA, SessionLocal

CONTENU = "bonjour je voulais savoir si vous aviez recu mon dossier"


def _charge(**remplacements):
    base = {"type_action": "reformuler", "scope": "selection", "contenu": CONTENU}
    base.update(remplacements)
    return base


def _nombre_appels_ia():
    with SessionLocal() as session:
        return len(session.execute(select(IA)).scalars().all())


# ── Scénario nominal ─────────────────────────────────────────────────────────


def test_ti40_generation_nominale_rend_la_suggestion_et_trace_l_appel(
    client, auth, utilisateur, creer_document, ollama_double
):
    ollama_double(retour=("Bonjour, avez-vous bien reçu mon dossier ?", 57))
    document = creer_document(utilisateur)

    reponse = client.post(f"/documents/{document}/ia/generer", json=_charge(), headers=auth)

    assert reponse.status_code == 201
    corps = reponse.get_json()
    assert corps["content_after"] == "Bonjour, avez-vous bien reçu mon dossier ?"
    assert corps["tokens_used"] == 57
    assert corps["id_ia"]

    with SessionLocal() as session:
        appel = session.execute(select(IA)).scalar_one()
    assert appel.type_action == "reformuler"
    assert appel.content_before == CONTENU
    assert appel.content_after == "Bonjour, avez-vous bien reçu mon dossier ?"
    assert appel.user_id == utilisateur
    assert appel.id_document == document


def test_la_suggestion_n_est_pas_ecrite_dans_le_document(
    client, auth, utilisateur, creer_document, ollama_double
):
    """
    Le cahier des charges impose un affichage « différencié » : la suggestion
    est proposée, jamais appliquée d'office. L'insertion est une action
    explicite de l'utilisateur, côté client.
    """
    from database.db import Document

    ollama_double()
    document = creer_document(utilisateur, contenu=CONTENU)
    client.post(f"/documents/{document}/ia/generer", json=_charge(), headers=auth)

    with SessionLocal() as session:
        assert session.get(Document, document).content == CONTENU


# ── Validation des entrées ───────────────────────────────────────────────────


def test_ti41_action_hors_liste_blanche_refusee(
    client, auth, utilisateur, creer_document, ollama_double
):
    """RG-06 — seules compléter, reformuler et corriger sont acceptées."""
    ollama_double()
    document = creer_document(utilisateur)
    reponse = client.post(
        f"/documents/{document}/ia/generer",
        json=_charge(type_action="traduire"),
        headers=auth,
    )
    assert reponse.status_code == 400
    assert _nombre_appels_ia() == 0


def test_ti42_perimetre_hors_liste_blanche_refuse(
    client, auth, utilisateur, creer_document, ollama_double
):
    ollama_double()
    document = creer_document(utilisateur)
    reponse = client.post(
        f"/documents/{document}/ia/generer", json=_charge(scope="page"), headers=auth
    )
    assert reponse.status_code == 400


def test_ti43_contenu_vide_refuse(client, auth, utilisateur, creer_document, ollama_double):
    ollama_double()
    document = creer_document(utilisateur)
    for contenu in ("", "   ", None):
        reponse = client.post(
            f"/documents/{document}/ia/generer", json=_charge(contenu=contenu), headers=auth
        )
        assert reponse.status_code == 400, f"contenu={contenu!r}"


def test_ti44_contenu_au_dela_de_la_borne_refuse(
    app, client, auth, utilisateur, creer_document, ollama_double
):
    """
    RG-08 — la borne est lue dans la configuration et non codée en dur : elle
    dépend de la machine d'exécution, puisque ce que celle-ci peut générer
    avant le délai maximum limite ce qu'elle peut accepter en entrée.
    """
    borne = app.config["IA_MAX_CONTENU_LENGTH"]
    ollama_double()
    document = creer_document(utilisateur)
    reponse = client.post(
        f"/documents/{document}/ia/generer",
        json=_charge(contenu="x" * (borne + 1)),
        headers=auth,
    )
    assert reponse.status_code == 400
    assert str(borne) in reponse.get_json()["error"]


def test_ti45_contenu_exactement_a_la_borne_accepte(
    app, client, auth, utilisateur, creer_document, ollama_double
):
    """
    La borne doit être inclusive. Un test à borne + 1 seul ne distingue pas un
    `>` d'un `>=` : il faut les deux côtés de la limite.
    """
    borne = app.config["IA_MAX_CONTENU_LENGTH"]
    ollama_double()
    document = creer_document(utilisateur)
    reponse = client.post(
        f"/documents/{document}/ia/generer",
        json=_charge(contenu="x" * borne),
        headers=auth,
    )
    assert reponse.status_code == 201


def test_ti46_instructions_trop_longues_refusees(
    client, auth, utilisateur, creer_document, ollama_double
):
    ollama_double()
    document = creer_document(utilisateur)
    reponse = client.post(
        f"/documents/{document}/ia/generer",
        json=_charge(instructions="x" * 501),
        headers=auth,
    )
    assert reponse.status_code == 400


def test_instructions_a_la_borne_acceptees(
    client, auth, utilisateur, creer_document, ollama_double
):
    ollama_double()
    document = creer_document(utilisateur)
    reponse = client.post(
        f"/documents/{document}/ia/generer",
        json=_charge(instructions="x" * 500),
        headers=auth,
    )
    assert reponse.status_code == 201


# ── Autorisation ─────────────────────────────────────────────────────────────


def test_ti47_generer_sur_le_document_d_autrui_rend_404(
    client, auth, autre_utilisateur, creer_document, ollama_double
):
    ollama_double()
    document_tiers = creer_document(autre_utilisateur)

    reponse = client.post(f"/documents/{document_tiers}/ia/generer", json=_charge(), headers=auth)
    assert reponse.status_code == 404
    assert _nombre_appels_ia() == 0


def test_ti51_generer_sans_authentification_rend_401(client, utilisateur, creer_document):
    document = creer_document(utilisateur)
    assert client.post(f"/documents/{document}/ia/generer", json=_charge()).status_code == 401


# ── Quota (RG-07) ────────────────────────────────────────────────────────────


def test_ti48_quota_atteint_rend_429(
    client, auth, utilisateur, creer_document, creer_appels_ia, ollama_double
):
    ollama_double()
    document = creer_document(utilisateur)
    creer_appels_ia(utilisateur, document, nombre=20, heures_avant=1)

    reponse = client.post(f"/documents/{document}/ia/generer", json=_charge(), headers=auth)

    assert reponse.status_code == 429
    assert "Quota" in reponse.get_json()["error"]
    assert _nombre_appels_ia() == 20, "aucun appel supplémentaire ne doit être enregistré"


def test_ti49_la_fenetre_de_quota_est_glissante(
    client, auth, utilisateur, creer_document, creer_appels_ia, ollama_double
):
    """
    19 appels récents et 1 appel vieux de 25 h : la fenêtre glissante ne
    compte que les 19, donc l'appel passe. Avec une remise à zéro à minuit,
    le résultat dépendrait de l'heure d'exécution du test.
    """
    ollama_double()
    document = creer_document(utilisateur)
    creer_appels_ia(utilisateur, document, nombre=19, heures_avant=2)
    creer_appels_ia(utilisateur, document, nombre=1, heures_avant=25)

    reponse = client.post(f"/documents/{document}/ia/generer", json=_charge(), headers=auth)
    assert reponse.status_code == 201


def test_le_quota_est_propre_a_chaque_utilisateur(
    client, auth, utilisateur, autre_utilisateur, creer_document, creer_appels_ia, ollama_double
):
    ollama_double()
    document_tiers = creer_document(autre_utilisateur)
    creer_appels_ia(autre_utilisateur, document_tiers, nombre=20, heures_avant=1)

    mon_document = creer_document(utilisateur)
    reponse = client.post(f"/documents/{mon_document}/ia/generer", json=_charge(), headers=auth)
    assert reponse.status_code == 201, "le quota d'un tiers ne doit pas bloquer le mien"


def test_le_quota_suit_la_limite_propre_au_compte(
    client, entetes, creer_utilisateur, creer_document, creer_appels_ia, ollama_double
):
    """Le plafond est lu sur le compte, pas codé en dur à 20."""
    ollama_double()
    bride = creer_utilisateur("bride@exemple.fr", quota=2)
    document = creer_document(bride)
    creer_appels_ia(bride, document, nombre=2, heures_avant=1)

    reponse = client.post(
        f"/documents/{document}/ia/generer",
        json=_charge(),
        headers=entetes("bride@exemple.fr"),
    )
    assert reponse.status_code == 429


# ── Panne du service d'inférence ─────────────────────────────────────────────


def test_ti50_ollama_injoignable_rend_502_sans_consommer_de_quota(
    client, auth, utilisateur, creer_document, ollama_double
):
    """
    Un appel qui échoue ne doit pas être facturé à l'utilisateur : sinon une
    panne d'Ollama épuiserait son quota sans lui rendre aucun service.
    """
    ollama_double(exception=RuntimeError("Impossible de joindre Ollama sur http://localhost:11434"))
    document = creer_document(utilisateur)

    reponse = client.post(f"/documents/{document}/ia/generer", json=_charge(), headers=auth)

    assert reponse.status_code == 502
    assert "Ollama" in reponse.get_json()["error"]
    assert _nombre_appels_ia() == 0, "aucune trace ne doit être écrite pour un appel échoué"


def test_un_delai_depasse_rend_aussi_502(client, auth, utilisateur, creer_document, ollama_double):
    ollama_double(exception=RuntimeError("Ollama a mis trop de temps à répondre"))
    document = creer_document(utilisateur)
    reponse = client.post(f"/documents/{document}/ia/generer", json=_charge(), headers=auth)
    assert reponse.status_code == 502


# ── Historique ───────────────────────────────────────────────────────────────


def test_ti52_l_historique_est_antichronologique(
    client, auth, utilisateur, creer_document, ollama_double
):
    ollama_double()
    document = creer_document(utilisateur)
    for action in ("reformuler", "corriger", "completer"):
        client.post(
            f"/documents/{document}/ia/generer",
            json=_charge(type_action=action),
            headers=auth,
        )

    entrees = client.get(f"/documents/{document}/ia/historique", headers=auth).get_json()

    assert len(entrees) == 3
    dates = [e["created_at"] for e in entrees]
    assert dates == sorted(dates, reverse=True), "la plus récente doit venir en premier"


def test_ti53_l_historique_du_document_d_autrui_rend_404(
    client, auth, autre_utilisateur, creer_document
):
    document_tiers = creer_document(autre_utilisateur)
    reponse = client.get(f"/documents/{document_tiers}/ia/historique", headers=auth)
    assert reponse.status_code == 404


def test_l_historique_d_un_document_sans_appel_est_vide(client, auth, utilisateur, creer_document):
    document = creer_document(utilisateur)
    assert client.get(f"/documents/{document}/ia/historique", headers=auth).get_json() == []
