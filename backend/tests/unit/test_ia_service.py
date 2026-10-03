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

from app.services.ia_service import (
    PROMPT_TEMPLATES,
    TEMPERATURE_PAR_DEFAUT,
    build_prompt,
    call_ollama,
    temperature_pour,
)


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


# ── Température par action ───────────────────────────────────────────────────

def test_temperature_corriger_est_la_plus_basse():
    """
    Corriger l'orthographe demande au modèle de ne rien changer d'autre. Une
    température élevée l'incite à reformuler au passage, c'est-à-dire
    exactement ce que le gabarit lui interdit. L'ordre entre les trois actions
    est donc une propriété à verrouiller, pas un réglage cosmétique.
    """
    assert temperature_pour("corriger") < temperature_pour("reformuler")
    assert temperature_pour("reformuler") < temperature_pour("completer")


def test_temperature_pour_une_action_inconnue_reste_conservatrice():
    assert temperature_pour("traduire") == TEMPERATURE_PAR_DEFAUT


def test_la_route_transmet_la_temperature_de_l_action(app, monkeypatch):
    """La température choisie doit réellement atteindre Ollama."""
    envoye = {}

    def _capture(*a, **k):
        envoye.update(k.get("json", {}))
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        call_ollama("un prompt", temperature=temperature_pour("corriger"))

    assert envoye["options"]["temperature"] == 0.1


# ── Fenêtre de contexte ──────────────────────────────────────────────────────

def test_call_ollama_transmet_num_ctx(app, monkeypatch):
    """
    Régression. Sans `num_ctx` explicite, Ollama applique un défaut de 4096
    jetons en deçà de 24 Gio de mémoire vidéo et **tronque silencieusement**
    au-delà : ni erreur, ni avertissement côté client. La coupe se faisant par
    l'avant, ce sont les consignes du gabarit qui disparaissent en premier, pas
    le texte de l'utilisateur — le modèle reçoit un document sans instruction.

    Ce test échoue si l'option est retirée.
    """
    envoye = {}

    def _capture(*a, **k):
        envoye.update(k.get("json", {}))
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        call_ollama("un prompt")

    assert "num_ctx" in envoye["options"], "num_ctx n'est pas transmis à Ollama"
    assert envoye["options"]["num_ctx"] == app.config["OLLAMA_NUM_CTX"]
    assert envoye["options"]["num_ctx"] > 4096, (
        "une fenêtre au défaut d'Ollama ne couvre pas la borne de contenu acceptée"
    )


def test_le_modele_et_le_delai_viennent_de_la_configuration(app, monkeypatch):
    """
    Le modèle dépend de la machine, pas du code : une machine sans carte
    graphique n'exécute pas le même que celle qui en a une.
    """
    envoye = {}

    def _capture(*a, **k):
        envoye.update({"json": k.get("json"), "timeout": k.get("timeout")})
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        call_ollama("un prompt")

    assert envoye["json"]["model"] == app.config["OLLAMA_MODEL"]
    assert envoye["timeout"] == app.config["OLLAMA_TIMEOUT"]


def test_la_borne_de_contenu_tient_dans_la_fenetre_de_contexte(app):
    """
    Cohérence des deux réglages. Reformuler produit à peu près autant de texte
    qu'il en reçoit : la fenêtre doit donc loger l'entrée ET la sortie. En
    comptant environ 3,7 caractères par jeton en français, la borne de contenu
    ne doit pas dépasser la moitié de la fenêtre.
    """
    jetons_entree = app.config["IA_MAX_CONTENU_LENGTH"] / 3.7
    assert jetons_entree * 2 < app.config["OLLAMA_NUM_CTX"], (
        f"IA_MAX_CONTENU_LENGTH={app.config['IA_MAX_CONTENU_LENGTH']} ne tient pas "
        f"avec sa réponse dans OLLAMA_NUM_CTX={app.config['OLLAMA_NUM_CTX']}"
    )


# Débit plancher retenu pour le dimensionnement : qwen3:4b sur processeur seul,
# sans carte graphique. C'est la machine la plus lente sur laquelle le projet
# doit tourner, donc celle qui fixe la borne.
JETONS_PAR_SECONDE_PLANCHER = 15
CARACTERES_PAR_JETON = 3.7


def test_la_borne_de_contenu_est_generable_avant_le_delai_maximum(app):
    """
    Cohérence entre la borne d'entrée et le délai maximum.

    Reformuler produit à peu près autant de texte qu'il en reçoit. Accepter
    plus de caractères que la machine ne sait en générer avant OLLAMA_TIMEOUT
    revient à promettre à l'utilisateur un service qui se terminera en 502 :
    la validation le laisse passer, et l'inférence dépasse le délai.

    Ce test a été ajouté après avoir constaté que la valeur initialement
    retenue (4 000 caractères) demandait 72 secondes de génération au débit
    plancher, pour un délai maximum de 60 secondes.
    """
    jetons_a_generer = app.config["IA_MAX_CONTENU_LENGTH"] / CARACTERES_PAR_JETON
    secondes = jetons_a_generer / JETONS_PAR_SECONDE_PLANCHER

    assert secondes < app.config["OLLAMA_TIMEOUT"], (
        f"IA_MAX_CONTENU_LENGTH={app.config['IA_MAX_CONTENU_LENGTH']} demande "
        f"~{secondes:.0f} s de génération à {JETONS_PAR_SECONDE_PLANCHER} jetons/s, "
        f"pour un OLLAMA_TIMEOUT de {app.config['OLLAMA_TIMEOUT']} s"
    )


# ── Messages d'erreur exploitables ───────────────────────────────────────────

class _ReponseEnErreur:
    """Double d'une réponse HTTP en erreur, telle que requests l'attache."""

    def __init__(self, statut, charge=None, texte=""):
        self.status_code = statut
        self._charge = charge
        self.text = texte

    def json(self):
        if self._charge is None:
            raise ValueError("pas de JSON")
        return self._charge


def _lever_http(statut, charge=None, texte=""):
    erreur = requests.exceptions.HTTPError(f"{statut} Client Error")
    erreur.response = _ReponseEnErreur(statut, charge, texte)

    def _post(*a, **k):
        raise erreur

    return _post


def test_un_404_nomme_le_modele_manquant_et_la_commande(app, monkeypatch):
    """
    Régression. Un 404 sur /api/generate ne signifie pas « endpoint absent »
    mais « modèle absent » : l'URL est bonne, c'est le modèle demandé qui n'est
    pas téléchargé sur cette machine.

    Avant correction, le message se réduisait à « Erreur Ollama: 404 Client
    Error: Not Found for url: ... » : la réponse d'Ollama, qui dit exactement
    quel modèle manque et quoi faire, était jetée.
    """
    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        _lever_http(404, {"error": "model 'qwen3:4b' not found, try pulling it first"}),
    )
    with app.app_context():
        with pytest.raises(RuntimeError) as capture:
            call_ollama("un prompt")

    message = str(capture.value)
    assert app.config["OLLAMA_MODEL"] in message, "le modèle manquant doit être nommé"
    assert "ollama pull" in message, "la commande à lancer doit être donnée"
    assert "not found" in message, "le message d'Ollama doit être conservé"


def test_une_erreur_serveur_conserve_le_detail_d_ollama(app, monkeypatch):
    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        _lever_http(500, {"error": "unexpected server error"}),
    )
    with app.app_context():
        with pytest.raises(RuntimeError, match="unexpected server error"):
            call_ollama("un prompt")


def test_une_reponse_d_erreur_sans_json_ne_fait_pas_echouer_le_traitement(app, monkeypatch):
    """Un service tiers n'est pas tenu de renvoyer du JSON, même en erreur."""
    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        _lever_http(503, charge=None, texte="<html>Service Unavailable</html>"),
    )
    with app.app_context():
        with pytest.raises(RuntimeError, match="503"):
            call_ollama("un prompt")


def test_le_detail_renvoye_est_borne_et_sur_une_seule_ligne(app, monkeypatch):
    """
    Le détail finit dans une réponse HTTP destinée à l'utilisateur : rien ne
    garantit la forme de ce que renvoie un service tiers, donc on le borne et
    on le remet sur une ligne plutôt que de le recopier tel quel.
    """
    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        _lever_http(500, {"error": "ligne un\nligne deux\n" + "x" * 500}),
    )
    with app.app_context():
        with pytest.raises(RuntimeError) as capture:
            call_ollama("un prompt")

    message = str(capture.value)
    assert "\n" not in message
    assert len(message) < 300
