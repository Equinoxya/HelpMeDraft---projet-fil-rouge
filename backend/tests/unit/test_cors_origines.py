"""
Politique d'origine croisée (CORS) — non-régression d'une panne réelle.

CE QUI S'EST PASSÉ : `.env.example` assignait « CORS_ORIGINS=http://localhost:8080 »,
la valeur du conteneur. Or ce même fichier est celui qu'on copie en
`backend/.env` pour un poste de développement, où le frontend est servi par Vite
sur le port 5173. Résultat sur un poste ainsi configuré :

    Access to XMLHttpRequest at 'http://localhost:5000/auth/register'
    from origin 'http://localhost:5173' has been blocked by CORS policy:
    No 'Access-Control-Allow-Origin' header is present

Inscription et connexion étaient impossibles. Et la panne était pénible à
diagnostiquer parce qu'elle ne ressemble pas à une erreur : le serveur répond
**200** à la requête préalable, simplement sans l'en-tête attendu. Aucune trace
côté serveur, aucune exception, aucun test rouge.

Ces tests verrouillent les trois points qui ont permis la panne.
"""

import pathlib
import re

import pytest

RACINE = pathlib.Path(__file__).resolve().parents[3]
ENV_EXEMPLE = RACINE / ".env.example"

# Les deux variables dont la bonne valeur DÉPEND de la façon de lancer
# l'application. Les assigner dans un fichier d'exemple commun aux deux, c'est
# en casser une.
VARIABLES_DEPENDANTES_DU_LANCEMENT = ("CORS_ORIGINS", "FRONTEND_URL")


@pytest.mark.parametrize("variable", VARIABLES_DEPENDANTES_DU_LANCEMENT)
def test_tu86_env_exemple_n_assigne_pas_les_variables_dependantes_du_lancement(variable):
    """
    `.env.example` ne doit pas assigner ces variables, commentaires exclus.

    Le fichier sert aux deux modes de lancement : copié en `backend/.env` pour un
    poste de développement, et en `.env` à la racine pour « docker compose up ».
    Une valeur écrite une seule fois y est donc fausse dans l'un des deux cas.

    Les deux valeurs par défaut sont déjà justes là où il faut — 5173 dans le
    code, 8080 dans docker-compose.yml. Le fichier d'exemple doit les laisser
    faire leur travail.
    """
    assignations = [
        ligne
        for ligne in ENV_EXEMPLE.read_text(encoding="utf-8").splitlines()
        if re.match(rf"^\s*{variable}\s*=", ligne)
    ]
    assert not assignations, (
        f"« {variable} » est assignée dans .env.example : {assignations}. "
        "Cette variable n'a pas la même valeur en local (Vite, port 5173) et en "
        "conteneur (nginx, port 8080) ; or le même fichier sert aux deux. "
        "La laisser commentée — les défauts de config.py et de docker-compose.yml "
        "sont corrects."
    )


def test_tu87_le_defaut_hors_conteneur_autorise_le_serveur_de_developpement(monkeypatch):
    """Sans CORS_ORIGINS dans l'environnement, Vite sur 5173 doit être autorisé."""
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    import importlib

    from app import config

    importlib.reload(config)
    assert "http://localhost:5173" in config.Config.CORS_ORIGINS


def test_tu88_le_preflight_porte_l_entete_pour_une_origine_autorisee(client):
    """
    La requête préalable d'inscription doit porter Access-Control-Allow-Origin.

    C'est l'en-tête dont l'ABSENCE constituait toute la panne. Un 200 ne suffit
    pas à conclure : le serveur répondait déjà 200 quand tout était cassé.
    """
    reponse = client.options(
        "/auth/register",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert reponse.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173", (
        "L'en-tête Access-Control-Allow-Origin est absent de la réponse au "
        f"préflight (statut {reponse.status_code}). Le navigateur refusera "
        "l'inscription et la connexion, sans qu'aucune erreur n'apparaisse côté "
        "serveur."
    )


def test_tu89_une_origine_refusee_est_journalisee(client, caplog):
    """
    Un refus d'origine doit laisser une trace EXPLOITABLE dans le journal.

    Sans elle, la panne est muette côté serveur — c'est ce qui l'a rendue longue
    à trouver. Le message doit nommer l'origine refusée et les origines admises.
    """
    import logging

    with caplog.at_level(logging.WARNING, logger="app"):
        client.post(
            "/auth/login",
            json={"email": "x@y.fr", "mdp": "MotDePasse1"},
            headers={"Origin": "http://localhost:8080"},
        )

    avertissements = [e.getMessage() for e in caplog.records if e.levelno >= logging.WARNING]
    assert any("Origine REFUSÉE" in m and "http://localhost:8080" in m for m in avertissements), (
        f"Aucun avertissement ne signale l'origine refusée. Journal observé : {avertissements}"
    )


def test_tu90_une_requete_sans_origine_ne_pollue_pas_le_journal(client, caplog):
    """
    Un appel sans en-tête Origin ne doit RIEN journaliser.

    curl, une sonde de santé ou un test n'envoient pas d'origine et ne sont pas
    concernés par la politique d'origine croisée. Sans ce filtre, le journal se
    remplirait d'avertissements pour des requêtes normales — et un journal qui
    crie tout le temps ne signale plus rien.
    """
    import logging

    with caplog.at_level(logging.WARNING, logger="app"):
        client.post("/auth/login", json={"email": "x@y.fr", "mdp": "MotDePasse1"})

    assert not [
        e.getMessage()
        for e in caplog.records
        if e.levelno >= logging.WARNING and "Origine REFUSÉE" in e.getMessage()
    ]
