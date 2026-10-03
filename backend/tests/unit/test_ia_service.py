"""
Tests unitaires du service d'intégration IA — TU-09 à TU-14.

Deux responsabilités testées séparément :
  - `build_prompt` : construction du prompt à partir du gabarit de l'action
    (c'est le « prompt engineering dynamique » exigé par le cahier des charges) ;
  - `call_ollama`  : dialogue avec le service d'inférence, et surtout sa
    traduction des pannes réseau en RuntimeError exploitable par la route.

Aucun appel réseau : `requests.post` est remplacé par un double.
"""
import json

import pytest
import requests

from app.services.ia_service import (
    PROMPT_TEMPLATES,
    TEMPERATURE_PAR_DEFAUT,
    _nettoyer_raisonnement,
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
    """
    Double d'une réponse Ollama en flux NDJSON.

    Ollama renvoie une ligne JSON par jeton, pas un objet unique : le double
    doit donc imiter `iter_lines`, et non `json()`. Un dictionnaire passé seul
    est traité comme un flux d'une seule ligne, ce qui garde lisibles les tests
    qui ne s'intéressent pas au découpage.
    """

    def __init__(self, charge):
        blocs = charge if isinstance(charge, list) else [{**charge, "done": True}]
        self._lignes = [
            json.dumps(bloc).encode("utf-8") for bloc in blocs
        ]

    def raise_for_status(self):
        return None

    def iter_lines(self):
        return iter(self._lignes)

    # `call_ollama` ouvre la réponse avec `with` pour garantir sa fermeture.
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


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


def test_tu13_call_ollama_traduit_un_delai_de_connexion_depasse(app, monkeypatch):
    """
    Un délai dépassé ne désigne plus une génération trop lente — plus aucun
    délai ne borne la lecture — mais une connexion qui n'aboutit pas. Le
    message le dit, et l'erreur reste une RuntimeError pour que la route la
    traduise en 502 plutôt qu'en 500.
    """
    def _connexion_trop_longue(*a, **k):
        raise requests.exceptions.ConnectTimeout()

    monkeypatch.setattr(
        "app.services.ia_service.requests.post", _connexion_trop_longue
    )
    with app.app_context():
        with pytest.raises(RuntimeError, match="Impossible de joindre Ollama"):
            call_ollama("un prompt")


def test_call_ollama_traduit_une_erreur_http(app, monkeypatch):
    def _erreur_http(*a, **k):
        raise requests.exceptions.HTTPError("500 Server Error")

    monkeypatch.setattr("app.services.ia_service.requests.post", _erreur_http)
    with app.app_context():
        with pytest.raises(RuntimeError, match="Erreur Ollama"):
            call_ollama("un prompt")


def test_call_ollama_borne_la_connexion_mais_pas_la_lecture(app, monkeypatch):
    """
    Les deux délais ne jouent pas le même rôle, et c'est la raison d'être du
    couple (connexion, lecture).

    Un délai sur la LECTURE coupait des générations qui aboutissaient :
    l'utilisateur recevait une erreur alors que rien n'avait échoué, juste
    parce que la machine était lente. Il est donc retiré.

    Un délai sur la CONNEXION reste indispensable : sans lui, un Ollama non
    lancé ferait attendre le serveur sur un socket qui ne répondra jamais.
    """
    appels = {}

    def _capture(*a, **k):
        appels.update(k)
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        delai_connexion = app.config["OLLAMA_CONNECT_TIMEOUT"]
        call_ollama("un prompt")

    assert delai_connexion > 0, "le délai de connexion ne doit pas être nul"
    assert appels.get("timeout") == (delai_connexion, None), (
        "requests.post doit recevoir un couple (connexion bornée, lecture "
        f"illimitée), reçu : {appels.get('timeout')!r}"
    )


# ── Lecture du flux NDJSON ───────────────────────────────────────────────────

def test_call_ollama_recompose_le_texte_depuis_le_flux(app, monkeypatch):
    """
    Le cas qui cassait toute génération.

    Avec `"stream": true`, Ollama renvoie une ligne JSON par jeton et non un
    objet unique. Le code appelait `response.json()` dessus, qui échoue avec
    « Extra data: line 2 column 1 » — et l'échec se produisait APRÈS le bloc
    de traduction des erreurs, donc la route renvoyait un 500 opaque.

    Les morceaux doivent être recollés dans l'ordre, sans séparateur ajouté.
    """
    flux = [
        {"response": "Bonjour", "done": False},
        {"response": ", je serai", "done": False},
        {"response": " en retard.", "done": False},
        {"response": "", "done": True, "prompt_eval_count": 30, "eval_count": 12},
    ]
    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        lambda *a, **k: _ReponseFactice(flux),
    )
    with app.app_context():
        texte, jetons = call_ollama("un prompt")

    assert texte == "Bonjour, je serai en retard."
    assert jetons == 42, "les compteurs ne figurent que sur la ligne done: true"


def test_call_ollama_demande_bien_un_flux(app, monkeypatch):
    """
    Les deux `stream` ne sont pas redondants : celui de la charge utile
    demande à Ollama de diffuser, celui de `requests` l'empêche d'accumuler
    tout le corps avant de nous le rendre. Sans le second, diffuser ne sert
    à rien.
    """
    envoye = {}

    def _capture(*a, **k):
        envoye.update(k)
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        call_ollama("un prompt")

    assert envoye["json"]["stream"] is True, "Ollama doit diffuser sa réponse"
    assert envoye["stream"] is True, "requests ne doit pas tamponner le corps"


def test_call_ollama_signale_une_erreur_survenue_pendant_le_flux(app, monkeypatch):
    """
    Une erreur peut arriver EN COURS de flux, après un statut 200 :
    `raise_for_status()` ne la verra jamais. Sans ce traitement, la ligne
    d'erreur serait silencieusement comptée comme du texte généré et
    enregistrée dans le document de l'utilisateur.
    """
    flux = [
        {"response": "Début", "done": False},
        {"error": "model runner has unexpectedly stopped"},
    ]
    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        lambda *a, **k: _ReponseFactice(flux),
    )
    with app.app_context():
        with pytest.raises(RuntimeError, match="model runner"):
            call_ollama("un prompt")


def test_call_ollama_refuse_un_flux_illisible(app, monkeypatch):
    """
    Un corps qui n'est pas du JSON ligne par ligne doit donner une
    RuntimeError — donc un 502 explicite — et non une exception non
    interprétée remontée en 500.
    """
    class _FluxCasse(_ReponseFactice):
        def iter_lines(self):
            return iter([b"<html>502 Bad Gateway</html>"])

    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        lambda *a, **k: _FluxCasse({"response": ""}),
    )
    with app.app_context():
        with pytest.raises(RuntimeError, match="illisible"):
            call_ollama("un prompt")


# ── Mode raisonnement ────────────────────────────────────────────────────────

def test_call_ollama_desactive_le_mode_raisonnement(app, monkeypatch):
    """
    Le réglage qui rendait l'IA inutilisable sur processeur seul.

    Un modèle à raisonnement produit un bloc <think>...</think> avant sa
    réponse, de taille à peu près constante : il réfléchit autant pour
    corriger « BJR » que pour reformuler trois pages. Mesuré sur qwen3:4b,
    cela faisait plusieurs minutes d'attente pour corriger une phrase de
    quarante caractères.

    Le champ est de PREMIER niveau et non une option : c'est ce qu'attend
    l'API d'Ollama.
    """
    envoye = {}

    def _capture(*a, **k):
        envoye.update(k.get("json", {}))
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        call_ollama("un prompt")

    assert envoye.get("think") is False, (
        "le mode raisonnement doit être désactivé : il coûte des minutes "
        "d'attente pour une tâche de réécriture"
    )
    assert "think" not in envoye["options"], (
        "think est un champ de premier niveau, pas une option d'inférence"
    )


def test_call_ollama_reessaie_sans_think_si_le_modele_ne_le_supporte_pas(
    app, monkeypatch
):
    """
    Ollama répond 400 « "<modèle>" does not support thinking » quand on passe
    `think` à un modèle qui n'a pas de mode raisonnement. Le modèle venant de
    la configuration, une machine peut tourner sur llama3.1 là où une autre
    tourne sur qwen3 : les deux doivent marcher sans réglage.

    L'utilisateur ne peut rien corriger lui-même ici, donc on refait l'appel
    sans le champ au lieu de remonter une erreur.
    """
    appels = []

    def _capture(*a, **k):
        charge = k.get("json", {})
        appels.append(charge)
        if "think" in charge:
            reponse = _ReponseEnErreur(
                400, {"error": '"llama3.1" does not support thinking'}
            )
            raise requests.exceptions.HTTPError(response=reponse)
        return _ReponseFactice({"response": "Texte généré."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        texte, _ = call_ollama("un prompt")

    assert texte == "Texte généré.", "la génération doit aboutir malgré le refus"
    assert len(appels) == 2, "il faut exactement un nouvel essai, pas une boucle"
    assert "think" not in appels[1], "le second essai doit omettre le champ"


def test_call_ollama_lit_le_detail_avant_de_liberer_la_connexion(app, monkeypatch):
    """
    Régression trouvée contre un vrai serveur HTTP, invisible pour un double.

    La réponse est obtenue en flux et ouverte avec `with`. Si le corps n'est
    lu qu'une fois sorti du bloc, la connexion est déjà libérée et le corps
    devient illisible : le diagnostic d'Ollama (« model not found », « does
    not support thinking ») est remplacé par un « 400 Client Error » muet.

    Ce double refuse de livrer son corps après fermeture, ce qu'un double
    ordinaire ne fait pas — c'est précisément ce qui avait laissé passer le
    bug.
    """
    class _CorpsFermable(_ReponseEnErreur):
        def __init__(self):
            super().__init__(400, {"error": '"llama3.1" does not support thinking'})
            self.ferme = False

        def raise_for_status(self):
            raise requests.exceptions.HTTPError("400 Client Error", response=self)

        def json(self):
            if self.ferme:
                raise ValueError("corps déjà consommé : connexion libérée")
            return self._charge

        def iter_lines(self):
            return iter([json.dumps({"response": "Texte.", "done": True}).encode()])

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.ferme = True
            return False

    appels = []

    def _capture(*a, **k):
        appels.append(k.get("json", {}))
        if "think" in k.get("json", {}):
            return _CorpsFermable()
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        texte, _ = call_ollama("un prompt")

    assert texte == "Texte.", (
        "le refus de think doit être reconnu alors que le corps n'est lisible "
        "qu'à l'intérieur du bloc with"
    )
    assert len(appels) == 2


def test_call_ollama_ne_masque_pas_les_autres_erreurs_400(app, monkeypatch):
    """
    Le nouvel essai ne doit se déclencher que sur le refus de `think`. Un 400
    pour une autre raison reste une erreur à remonter, sinon on la redemande
    une seconde fois pour rien avant de la signaler.
    """
    appels = []

    def _capture(*a, **k):
        appels.append(k.get("json", {}))
        reponse = _ReponseEnErreur(400, {"error": "invalid options: num_ctx"})
        raise requests.exceptions.HTTPError(response=reponse)

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        with pytest.raises(RuntimeError, match="num_ctx"):
            call_ollama("un prompt")

    assert len(appels) == 1, "un 400 sans rapport avec think ne doit pas être rejoué"


# ── Nettoyage du bloc de raisonnement ────────────────────────────────────────
#
# Cas réel observé : qwen3:4b sur une version d'Ollama antérieure à la 0.9.
# Le champ `think` de l'API y est un champ inconnu, donc ignoré en silence ; le
# modèle a raisonné quand même, et son monologue — plusieurs pages, en anglais,
# pour corriger une phrase de quarante caractères — est arrivé COLLÉ au texte
# utile, dans le champ que l'application propose d'insérer dans le document.

def test_nettoyer_raisonnement_garde_ce_qui_suit_la_balise():
    brut = (
        "<think>\nOkay, the user wants me to reformulate. Let me break it down.\n"
        "BJR is an abbreviation for bonjour...\n</think>\n\n"
        "Bonjour, je serai en retard. Désolée."
    )
    assert _nettoyer_raisonnement(brut) == "Bonjour, je serai en retard. Désolée."


def test_nettoyer_raisonnement_coupe_apres_le_dernier_bloc():
    """Un modèle peut émettre plusieurs blocs : seul le dernier compte."""
    brut = "<think>premier</think>brouillon<think>second</think>La réponse."
    assert _nettoyer_raisonnement(brut) == "La réponse."


def test_nettoyer_raisonnement_sur_un_bloc_jamais_referme():
    """
    Génération interrompue au milieu du raisonnement : il n'y a aucune réponse
    à en tirer, et surtout rien qui doive être proposé pour insertion.
    """
    assert _nettoyer_raisonnement("<think>je réfléchis encore et enc") == ""


def test_nettoyer_raisonnement_ne_touche_pas_un_texte_normal():
    """Le cas de loin le plus fréquent ne doit rien subir."""
    assert _nettoyer_raisonnement("  Bonjour, je serai en retard.  ") == (
        "Bonjour, je serai en retard."
    )


def test_call_ollama_ne_renvoie_jamais_le_raisonnement(app, monkeypatch):
    """
    Le bout en bout du cas observé : le bloc arrive découpé à travers le flux,
    exactement comme Ollama le livre, et ne doit pas ressortir.
    """
    flux = [
        {"response": "<think>\nOkay, let's tackle", "done": False},
        {"response": " this. BJR means bonjour.", "done": False},
        {"response": "\n</think>\n\nBonjour, je serai", "done": False},
        {"response": " en retard. Désolée.", "done": False},
        {"response": "", "done": True, "prompt_eval_count": 50, "eval_count": 900},
    ]
    monkeypatch.setattr(
        "app.services.ia_service.requests.post",
        lambda *a, **k: _ReponseFactice(flux),
    )
    with app.app_context():
        texte, jetons = call_ollama("un prompt")

    assert texte == "Bonjour, je serai en retard. Désolée."
    assert "<think>" not in texte and "</think>" not in texte
    assert jetons == 950, (
        "les jetons de raisonnement restent comptés : ils ont bien été "
        "générés, et c'est ce qui explique l'attente facturée au quota"
    )


# ── Le mode raisonnement ne se désactive pas par le prompt ───────────────────
#
# Les trois tests de la consigne /no_think ont été supprimés avec elle.
# Mesuré sur Ollama 0.35.1 avec qwen3:4b, en tête de prompt comme en fin : le
# modèle lit la consigne comme du TEXTE, la commente dans sa réflexion, puis
# la recopie dans sa réponse. Elle ne désactivait rien et polluait le résultat.
#
# Le projet a donc changé de modèle plutôt que de consigne — voir
# OLLAMA_MODEL dans config.py. Un modèle sans mode raisonnement n'a rien à
# désactiver.


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

def test_call_ollama_maintient_le_modele_en_memoire(app, monkeypatch):
    """
    Le chargement du modèle domine complètement le temps de réponse. Mesuré
    sur une machine de développement, même modèle et même prompt :

        appel à froid   427,66 s dont 426,9 s de chargement
        appel à chaud     0,19 s dont     0 s de chargement

    Le défaut d'Ollama décharge le modèle après 5 minutes, ce qui ne convient
    pas à un usage par intermittence : entre deux corrections espacées d'un
    quart d'heure, l'utilisateur repaie le chargement intégralement.

    Le champ est de PREMIER niveau, pas une option d'inférence.
    """
    envoye = {}

    def _capture(*a, **k):
        envoye.update(k.get("json", {}))
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        call_ollama("un prompt")

    assert envoye.get("keep_alive") == app.config["OLLAMA_KEEP_ALIVE"], (
        "le modèle doit être maintenu en mémoire entre deux appels"
    )
    assert "keep_alive" not in envoye["options"], (
        "keep_alive est un champ de premier niveau, pas une option d'inférence"
    )


def test_la_fenetre_de_contexte_est_dimensionnee_pas_genereuse(app):
    """
    La fenêtre doit être assez grande, et PAS PLUS. Les deux sens comptent.

    Trop petite, Ollama tronque en silence. Trop grande, le cache d'attention
    à allouer au chargement grossit, et sur une machine dont la RAM est juste
    cela déclenche du va-et-vient disque. Mesuré sur une machine de
    développement, même modèle et même prompt :

        num_ctx=4096   chargement   20,5 s
        num_ctx=8192   chargement  426,9 s

    Sept minutes pour une génération de 0,2 seconde. Ce test a été ajouté
    après ce constat, en remplacement d'une assertion « num_ctx > 4096 » qui
    encodait précisément l'erreur : elle traitait une fenêtre généreuse comme
    une précaution gratuite.
    """
    besoin = (
        app.config["IA_MAX_CONTENU_LENGTH"] / CARACTERES_PAR_JETON  # entrée
        + 70                                                        # gabarit
        + app.config["IA_MAX_CONTENU_LENGTH"] / CARACTERES_PAR_JETON  # sortie
    )
    fenetre = app.config["OLLAMA_NUM_CTX"]

    assert fenetre > besoin, (
        f"OLLAMA_NUM_CTX={fenetre} ne loge pas les ~{besoin:.0f} jetons requis "
        f"par IA_MAX_CONTENU_LENGTH={app.config['IA_MAX_CONTENU_LENGTH']} : "
        "Ollama tronquerait en silence, par l'avant, donc les consignes avant "
        "le texte"
    )
    assert fenetre < besoin * 4, (
        f"OLLAMA_NUM_CTX={fenetre} dépasse de plus de 4 fois le besoin réel "
        f"(~{besoin:.0f} jetons). Une fenêtre surdimensionnée n'est pas une "
        "précaution gratuite : elle alourdit le chargement du modèle, qui "
        "domine déjà le temps de réponse"
    )


def test_le_modele_et_le_delai_viennent_de_la_configuration(app, monkeypatch):
    """
    Le modèle dépend de la machine, pas du code : une machine sans carte
    graphique n'exécute pas le même que celle qui en a une. Le délai de
    connexion suit la même règle.
    """
    envoye = {}

    def _capture(*a, **k):
        envoye.update({"json": k.get("json"), "timeout": k.get("timeout")})
        return _ReponseFactice({"response": "Texte."})

    monkeypatch.setattr("app.services.ia_service.requests.post", _capture)
    with app.app_context():
        call_ollama("un prompt")

    assert envoye["json"]["model"] == app.config["OLLAMA_MODEL"]
    assert envoye["timeout"] == (app.config["OLLAMA_CONNECT_TIMEOUT"], None)


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


# Attente maximale qu'on estime acceptable devant un compteur de progression,
# en secondes. Ce n'est plus un délai technique — aucun délai ne coupe
# l'inférence — mais une borne d'expérience utilisateur : au-delà, on ne peut
# plus raisonnablement demander à quelqu'un de patienter.
ATTENTE_MAX_SECONDES = 90


def test_la_borne_de_contenu_reste_une_attente_acceptable(app):
    """
    Cohérence entre la borne d'entrée et le temps d'attente annoncé.

    Reformuler produit à peu près autant de texte qu'il en reçoit. Depuis le
    retrait du délai de lecture, dépasser la borne ne produit plus un 502 mais
    une attente : le risque a changé de nature, pas disparu. Accepter
    10 000 caractères sur une machine sans carte graphique, c'est afficher un
    compteur de trois minutes.

    Ce test garde donc la même fonction qu'avant — empêcher de relever
    IA_MAX_CONTENU_LENGTH sans regarder le débit de la machine — en mesurant
    cette fois l'attente et non le délai dépassé.
    """
    jetons_a_generer = app.config["IA_MAX_CONTENU_LENGTH"] / CARACTERES_PAR_JETON
    secondes = jetons_a_generer / JETONS_PAR_SECONDE_PLANCHER

    assert secondes < ATTENTE_MAX_SECONDES, (
        f"IA_MAX_CONTENU_LENGTH={app.config['IA_MAX_CONTENU_LENGTH']} demande "
        f"~{secondes:.0f} s de génération à {JETONS_PAR_SECONDE_PLANCHER} jetons/s, "
        f"au-delà des {ATTENTE_MAX_SECONDES} s d'attente jugées acceptables"
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
