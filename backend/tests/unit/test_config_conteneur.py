"""
Réglages que la mise en conteneur a rendus configurables.

Chacun était une valeur EN DUR qui marchait sur un poste de développement et
cassait ailleurs, sans message d'erreur exploitable. Ces tests existent pour
qu'on ne les y remette pas.
"""
import importlib
import os

import pytest


def _recharger_config():
    """Recharge app.config, dont les valeurs sont lues à l'import du module."""
    import app.config
    return importlib.reload(app.config).Config


@pytest.fixture
def config_propre():
    """Restaure l'environnement après chaque test, et recharge la config."""
    avant = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(avant)
    _recharger_config()


# ── Origines CORS ────────────────────────────────────────────────────────────

def test_les_origines_cors_par_defaut_sont_celles_du_poste_de_dev(config_propre):
    """
    Le défaut doit reproduire l'ancienne valeur en dur : un poste de
    développement existant ne doit rien avoir à changer.
    """
    os.environ.pop("CORS_ORIGINS", None)
    assert _recharger_config().CORS_ORIGINS == ["http://localhost:5173"]


def test_les_origines_cors_se_configurent(config_propre):
    """
    En conteneur, le frontend est servi par nginx sur un autre port. Sans ce
    réglage, le navigateur voyait toutes ses requêtes refusées par la politique
    d'origine croisée — sans aucune erreur côté serveur pour l'expliquer.
    """
    os.environ["CORS_ORIGINS"] = "http://localhost:8080"
    assert _recharger_config().CORS_ORIGINS == ["http://localhost:8080"]


def test_plusieurs_origines_cors_se_separent_par_des_virgules(config_propre):
    """Un même backend peut servir le poste de dev ET la pile conteneurisée."""
    os.environ["CORS_ORIGINS"] = "http://localhost:8080, http://localhost:5173"
    assert _recharger_config().CORS_ORIGINS == [
        "http://localhost:8080",
        "http://localhost:5173",
    ]


def test_les_origines_cors_ignorent_les_entrees_vides(config_propre):
    """
    Une virgule en trop est vite arrivée dans un .env. Une chaîne vide dans la
    liste serait une origine que Flask-CORS ne saurait pas interpréter.
    """
    os.environ["CORS_ORIGINS"] = "http://localhost:8080,,  ,"
    assert _recharger_config().CORS_ORIGINS == ["http://localhost:8080"]


def test_l_application_utilise_bien_la_configuration_cors(app):
    """
    Le réglage doit être LU par create_app. Il a longtemps existé une valeur en
    dur dans create_app, que la configuration ne pouvait pas remplacer.
    """
    assert app.config["CORS_ORIGINS"], "les origines doivent être renseignées"
    assert isinstance(app.config["CORS_ORIGINS"], list)
