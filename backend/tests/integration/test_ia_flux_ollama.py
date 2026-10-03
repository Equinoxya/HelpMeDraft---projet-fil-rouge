"""
Tests d'intégration du dialogue avec Ollama — contre un VRAI serveur HTTP.

POURQUOI CES TESTS EXISTENT EN PLUS DES TESTS UNITAIRES

Les tests unitaires de `ia_service` remplacent `requests.post` par un double.
C'est rapide et suffisant pour vérifier la traduction des erreurs, mais un
double répond toujours gentiment : il accepte `json()` à tout moment, ne
découpe pas ses octets, et ne libère jamais de connexion.

Deux bugs réels sont passés sous ces doubles :

  1. `"stream": true` a été activé côté charge utile sans adapter la lecture.
     Ollama renvoie alors une ligne JSON par jeton, et `response.json()`
     échouait sur « Extra data: line 2 column 1 » — après le bloc de
     traduction des erreurs, donc en 500 opaque. Toute génération était
     cassée.
  2. Le détail de l'erreur d'Ollama était lu APRÈS la sortie du bloc `with`.
     En flux, la connexion est alors libérée et le corps devient illisible :
     « model not found » et « does not support thinking » disparaissaient au
     profit d'un « 400 Client Error » sans information.

Ces deux cas ne sont visibles que face à un vrai serveur. D'où ce fichier :
un `http.server` minimal qui imite /api/generate, pour exercer la vraie pile
HTTP de `requests`.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from app.services.ia_service import call_ollama

# Flux volontairement découpé en plein milieu des mots, avec un tiret cadratin
# et des accents : c'est là qu'un découpage d'octets mal géré se verrait.
FLUX_NOMINAL = [
    {"response": "Bonjour, je ", "done": False},
    {"response": "ser", "done": False},
    {"response": "ai en retard", "done": False},
    {"response": " — désolée.", "done": False},
    {"response": "", "done": True, "prompt_eval_count": 30, "eval_count": 12},
]
TEXTE_ATTENDU = "Bonjour, je serai en retard — désolée."


class _FauxOllama:
    """Serveur HTTP qui imite /api/generate, sur un port libre choisi par l'OS."""

    def __init__(self, flux=None, refuse_think=False, statut_erreur=None, erreur=None):
        self.flux = flux if flux is not None else FLUX_NOMINAL
        self.refuse_think = refuse_think
        self.statut_erreur = statut_erreur
        self.erreur = erreur
        self.corps_recus = []
        faux = self

        class Handler(BaseHTTPRequestHandler):
            # HTTP/1.0 : la connexion se ferme après chaque réponse. En
            # HTTP/1.1, requests garde la connexion ouverte et le fil du
            # serveur reste à l'attendre, ce qui bloque l'arrêt du test.
            protocol_version = "HTTP/1.0"

            def do_POST(self):
                corps = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                faux.corps_recus.append(corps)

                if faux.statut_erreur is not None:
                    return self._erreur(faux.statut_erreur, faux.erreur)

                if faux.refuse_think and "think" in corps:
                    # Message d'Ollama mot pour mot pour un modèle sans mode
                    # raisonnement.
                    return self._erreur(400, f'"{corps["model"]}" does not support thinking')

                charge = b"".join(json.dumps(bloc).encode("utf-8") + b"\n" for bloc in faux.flux)
                self.send_response(200)
                self.send_header("Content-Type", "application/x-ndjson")
                self.send_header("Content-Length", str(len(charge)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(charge)

            def _erreur(self, statut, message):
                charge = json.dumps({"error": message}).encode("utf-8")
                self.send_response(statut)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(charge)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(charge)

            def log_message(self, *args):
                pass  # pas de bruit dans la sortie des tests

        # Multi-thread : un serveur mono-thread ne traite qu'une connexion à
        # la fois et son arrêt attend la fin de celle en cours.
        self._serveur = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._serveur.daemon_threads = True
        self.url = f"http://127.0.0.1:{self._serveur.server_port}"

    def __enter__(self):
        self._fil = threading.Thread(target=self._serveur.serve_forever, daemon=True)
        self._fil.start()
        return self

    def __exit__(self, *exc):
        self._serveur.shutdown()
        self._serveur.server_close()
        self._fil.join(timeout=5)
        return False


@pytest.fixture
def ollama(app):
    """Branche l'application sur un faux Ollama le temps d'un test."""

    def _brancher(**kwargs):
        faux = _FauxOllama(**kwargs)
        app.config["OLLAMA_URL"] = faux.url
        return faux

    return _brancher


def test_le_flux_ndjson_est_recompose_accents_compris(app, ollama):
    """
    Le cas qui cassait toute génération. Les morceaux doivent être recollés
    dans l'ordre, sans séparateur ajouté, et les caractères multi-octets
    doivent survivre au découpage du flux.
    """
    with ollama():
        with app.app_context():
            texte, jetons = call_ollama("corrige : BJR")

    assert texte == TEXTE_ATTENDU
    assert jetons == 42, "les compteurs ne figurent que sur la ligne done: true"


def test_le_mode_raisonnement_est_desactive_dans_la_vraie_requete(app, ollama):
    """
    Le réglage qui rendait l'IA inutilisable sur processeur seul : un modèle à
    raisonnement « réfléchit » autant pour corriger « BJR » que pour
    reformuler trois pages.
    """
    with ollama() as faux:
        with app.app_context():
            call_ollama("corrige : BJR")

    corps = faux.corps_recus[0]
    assert corps["think"] is False, "think doit être envoyé à false"
    assert corps["stream"] is True, "la réponse doit être demandée en flux"
    assert "think" not in corps["options"], "think est un champ de premier niveau"

    # Le chargement du modèle domine le temps de réponse : 426,9 s sur les
    # 427,66 s d'un appel à froid mesuré, contre 0,19 s à chaud. Ces deux
    # réglages sont donc ce qui sépare sept minutes de deux dixièmes de
    # seconde — ils doivent partir sur le réseau, pas seulement exister dans
    # la configuration.
    assert corps["keep_alive"] == app.config["OLLAMA_KEEP_ALIVE"]
    assert corps["options"]["num_ctx"] == app.config["OLLAMA_NUM_CTX"]


def test_un_modele_sans_mode_raisonnement_aboutit_quand_meme(app, ollama):
    """
    Ollama répond 400 « does not support thinking » sur llama3.1 ou mistral.
    Le modèle venant de la configuration, les deux familles doivent marcher
    sans réglage : le service refait l'appel sans le champ.

    Ce test vérifie aussi, indirectement, que le détail de l'erreur est lu
    avant la libération de la connexion — sans quoi le refus ne serait pas
    reconnu et la génération échouerait.
    """
    with ollama(refuse_think=True) as faux:
        with app.app_context():
            app.config["OLLAMA_MODEL"] = "llama3.1"
            texte, _ = call_ollama("corrige : BJR")

    assert texte == TEXTE_ATTENDU, "la génération doit aboutir malgré le refus"
    assert len(faux.corps_recus) == 2, "un seul nouvel essai, pas une boucle"
    assert "think" not in faux.corps_recus[1], "le second essai omet le champ"


def test_le_diagnostic_d_ollama_survit_a_la_lecture_en_flux(app, ollama):
    """
    Régression. Le corps d'une réponse en erreur doit être lu AVANT la sortie
    du bloc `with`, sinon la connexion est libérée et le message d'Ollama est
    perdu. Ici, le modèle manquant doit être nommé dans l'erreur remontée.
    """
    with ollama(
        statut_erreur=404,
        erreur="model 'qwen3:4b' not found, try pulling it first",
    ):
        with app.app_context():
            with pytest.raises(RuntimeError) as capture:
                call_ollama("corrige : BJR")

    message = str(capture.value)
    assert "ollama pull" in message, "l'erreur doit donner la commande à lancer"
    assert "not found" in message, "le diagnostic d'Ollama doit survivre à la lecture en flux"


def test_un_ollama_ancien_qui_ignore_think_ne_pollue_pas_le_resultat(app, ollama):
    """
    Cas réel observé sur qwen3:4b avec un Ollama antérieur à la 0.9.

    Dans ces versions, `think` est un champ inconnu : Ollama l'ignore SANS
    RIEN DIRE, le modèle raisonne quand même, et son monologue arrive COLLÉ au
    texte utile — ce n'est que depuis la 0.9 qu'il est renvoyé à part. Sans
    nettoyage, l'application proposait d'insérer plusieurs pages de monologue
    dans le document de l'utilisateur.

    Ce faux serveur reproduit ce comportement : il accepte `think` sans
    broncher et renvoie le bloc malgré tout.
    """
    flux = [
        {"response": "<think>\nOkay, let's tackle this. BJR", "done": False},
        {"response": " is an abbreviation for bonjour.", "done": False},
        {"response": " Let me check the typos.\n</think>", "done": False},
        {"response": "\n\nBonjour, je serai en retard. Désolée.", "done": False},
        {"response": "", "done": True, "prompt_eval_count": 50, "eval_count": 900},
    ]
    with ollama(flux=flux) as faux:
        with app.app_context():
            app.config["OLLAMA_MODEL"] = "qwen3:4b"
            texte, jetons = call_ollama("corrige : BJR")

    assert texte == "Bonjour, je serai en retard. Désolée."
    assert "<think>" not in texte and "</think>" not in texte

    # Le champ `think` doit bien être parti sur le réseau. La consigne de
    # prompt /no_think, elle, a été retirée du projet : mesurée inopérante sur
    # Ollama 0.35.1, elle était recopiée dans la réponse au lieu de désactiver
    # quoi que ce soit.
    corps = faux.corps_recus[0]
    assert corps["think"] is False
    assert "/no_think" not in corps["prompt"], (
        "la consigne ne doit plus être envoyée : elle ressortait dans le texte"
    )

    assert jetons == 950, (
        "les jetons de raisonnement restent comptés au quota : ils ont bien "
        "été générés, et c'est ce qui explique l'attente"
    )


def test_une_erreur_en_cours_de_flux_n_est_pas_prise_pour_du_texte(app, ollama):
    """
    Une erreur peut arriver après un statut 200, au milieu du flux :
    `raise_for_status()` ne la verra jamais. Sans traitement, la ligne
    d'erreur serait comptée comme du texte généré puis proposée à
    l'utilisateur pour insertion dans son document.
    """
    flux = [
        {"response": "Début de phrase", "done": False},
        {"error": "model runner has unexpectedly stopped"},
    ]
    with ollama(flux=flux):
        with app.app_context():
            with pytest.raises(RuntimeError, match="model runner"):
                call_ollama("corrige : BJR")
