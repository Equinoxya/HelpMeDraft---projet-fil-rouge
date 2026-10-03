"""
Tests unitaires du service d'intégration IA — TU-09 à TU-14.

Deux responsabilités testées séparément :
  - `build_prompt` : construction du prompt à partir du gabarit de l'action
    (c'est le « prompt engineering dynamique » exigé par le cahier des charges) ;
  - `call_ollama`  : dialogue avec le service d'inférence, et surtout sa
    traduction des pannes réseau en RuntimeError exploitable par la route.

Aucun appel réseau : `requests.post` est remplacé par un double.
"""
import pytest
import requests

from app.services.ia_service import PROMPT_TEMPLATES, build_prompt, call_ollama


# ── Construction du prompt ───────────────────────────────────────────────────

@pytest.mark.parametrize("action", ["reformuler", "corriger", "completer"])
def test_tu09_build_prompt_insere_le_contenu_dans_le_gabarit(action):
    prompt = build_prompt(action, "Le texte de l'utilisateur.")
    assert "Le texte de l'utilisateur." in prompt
    assert prompt.startswith(PROMPT_TEMPLATES[action][:30])


def test_tu10_build_prompt_refuse_une_action_inconnue():
    with pytest.raises(ValueError, match="Type d'action inconnu"):
        build_prompt("traduire", "Un texte.")


def test_tu11_build_prompt_ajoute_la_consigne_particuliere():
    prompt = build_prompt("reformuler", "Un texte.", "Garder le vouvoiement.")
    assert "Garder le vouvoiement." in prompt
    assert prompt.index("Un texte.") < prompt.index("Garder le vouvoiement."), (
        "la consigne doit être ajoutée après le contenu, pas avant"
    )


def test_build_prompt_sans_consigne_n_ajoute_rien():
    assert "Consigne particulière" not in build_prompt("corriger", "Un texte.")


@pytest.mark.parametrize("consigne", ["", None])
def test_build_prompt_ignore_une_consigne_vide(consigne):
    assert "Consigne particulière" not in build_prompt("corriger", "Un texte.", consigne)


# ── Appel au service d'inférence ─────────────────────────────────────────────

class _ReponseFactice:
    def __init__(self, charge):
        self._charge = charge

    def raise_for_status(self):
        return None

    def json(self):
        return self._charge


def test_tu14_call_ollama_renvoie_le_texte_et_la_somme_des_jetons(app, monkeypatch):
    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        lambda *a, **k: _ReponseFactice(
            {"response": "  Texte généré.  ", "prompt_eval_count": 30, "eval_count": 12}
        ),
    )
    with app.app_context():
        texte, jetons = call_ollama("un prompt")

    assert texte == "Texte généré.", "la réponse doit être débarrassée des espaces"
    assert jetons == 42, "les jetons comptés sont la somme du prompt et de la génération"


def test_call_ollama_tolere_une_reponse_sans_compteurs(app, monkeypatch):
    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        lambda *a, **k: _ReponseFactice({"response": "Texte."}),
    )
    with app.app_context():
        texte, jetons = call_ollama("un prompt")
    assert (texte, jetons) == ("Texte.", 0)


def test_tu12_call_ollama_traduit_une_connexion_refusee(app, monkeypatch):
    def _refus(*a, **k):
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr("app.services.ia_service.requests.post", _refus)
    with app.app_context():
        with pytest.raises(RuntimeError, match="Impossible de joindre Ollama"):
            call_ollama("un prompt")


def test_tu13_call_ollama_traduit_un_delai_depasse(app, monkeypatch):
    def _trop_long(*a, **k):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr("app.services.ia_service.requests.post", _trop_long)
    with app.app_context():
        with pytest.raises(RuntimeError, match="trop de temps"):
            call_ollama("un prompt")


def test_call_ollama_traduit_une_erreur_http(app, monkeypatch):
    def _erreur_http(*a, **k):
        raise requests.exceptions.HTTPError("500 Server Error")

    monkeypatch.setattr("app.services.ia_service.requests.post", _erreur_http)
    with app.app_context():
        with pytest.raises(RuntimeError, match="Erreur Ollama"):
            call_ollama("un prompt")


def test_call_ollama_envoie_un_delai_maximum(app, monkeypatch):
    """
    Un appel sans délai maximum bloquerait le processus serveur tant
    qu'Ollama ne répond pas : une panne du modèle deviendrait une panne de
    l'application entière.
    """
    appels = {}

    def _capture(*a, **k):
        appels.update(k)
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        call_ollama("un prompt")

    assert appels.get("timeout"), "aucun délai maximum n'est passé à requests.post"
