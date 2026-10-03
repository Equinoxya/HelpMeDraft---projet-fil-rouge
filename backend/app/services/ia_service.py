import requests
from flask import current_app

# Température par action, et non une valeur unique.
#
# Les trois actions n'appellent pas la même liberté. Corriger l'orthographe
# demande au modèle de ne RIEN changer d'autre : une température élevée l'incite
# à reformuler au passage, c'est-à-dire exactement ce qu'on lui a interdit.
# Compléter, à l'inverse, est une tâche de rédaction où un peu de variété est
# souhaitable. Une valeur unique de 0,7 pour les trois, comme c'était le cas,
# servait bien la dernière et desservait la première.
TEMPERATURES = {
    "corriger": 0.1,
    "reformuler": 0.3,
    "completer": 0.7,
}
TEMPERATURE_PAR_DEFAUT = 0.3

PROMPT_TEMPLATES = {
    "reformuler": (
        "Tu es un assistant de rédaction de documents professionnels. "
        "Reformule le texte suivant pour le rendre plus clair et plus professionnel, "
        "sans changer son sens ni ajouter d'informations nouvelles. "
        "Réponds uniquement avec le texte reformulé, sans commentaire ni introduction.\n\n"
        "Texte à reformuler :\n{contenu}"
    ),
    "corriger": (
        "Tu es un correcteur professionnel. Corrige les fautes d'orthographe, de grammaire "
        "et de syntaxe du texte suivant, sans changer son sens ni son style. "
        "Réponds uniquement avec le texte corrigé, sans commentaire ni introduction.\n\n"
        "Texte à corriger :\n{contenu}"
    ),
    "completer": (
        "Tu es un assistant de rédaction de documents professionnels. "
        "Complète le texte suivant de façon cohérente avec ce qui précède, "
        "en respectant le ton et le sujet. "
        "Réponds uniquement avec la suite proposée, sans répéter le texte existant.\n\n"
        "Texte à compléter :\n{contenu}"
    ),
}



def build_prompt(type_action: str, contenu: str, instructions: str | None = None) -> str:
    template = PROMPT_TEMPLATES.get(type_action)
    if template is None:
        raise ValueError(f"Type d'action inconnu: {type_action}")
    prompt = template.format(contenu = contenu)
    if instructions:
        prompt += f"\n\nConsigne particulière à respecter: {instructions}"
    return prompt

def temperature_pour(type_action: str) -> float:
    """Température d'inférence adaptée à l'action demandée."""
    return TEMPERATURES.get(type_action, TEMPERATURE_PAR_DEFAUT)


def _detail_ollama(response) -> str:
    """
    Extrait le message d'erreur qu'Ollama place dans le corps de sa réponse.

    `raise_for_status()` ne lève qu'avec la ligne de statut : « 404 Client
    Error: Not Found for url: ... ». La raison réelle — « model 'qwen3:4b' not
    found, try pulling it first » — est dans le CORPS, qui était jusqu'ici
    jeté. Ollama donnait le diagnostic, le code l'effaçait.

    Le texte est borné et remis sur une ligne : il finit dans une réponse HTTP
    destinée à l'utilisateur, et rien ne garantit la forme de ce que renvoie un
    service tiers.
    """
    if response is None:
        return ""
    try:
        detail = (response.json() or {}).get("error", "")
    except ValueError:
        detail = response.text or ""
    return " ".join(str(detail).split())[:200]


def _erreur_http(exception, model: str) -> str:
    """Construit un message exploitable à partir d'une réponse HTTP en erreur."""
    response = getattr(exception, "response", None)
    detail = _detail_ollama(response)
    statut = getattr(response, "status_code", None)

    # 404 sur /api/generate ne veut pas dire « endpoint absent » mais « modèle
    # absent » : l'URL est bonne, c'est le modèle demandé qui n'est pas
    # téléchargé sur cette machine. Le cas est fréquent dès qu'on change de
    # poste, puisque le modèle vient de la configuration et non du dépôt.
    if statut == 404:
        message = (
            f"Le modèle « {model} » est introuvable sur le serveur Ollama. "
            f"Téléchargez-le avec : ollama pull {model}"
        )
        return f"{message} (Ollama : {detail})" if detail else message

    if detail:
        return f"Erreur Ollama ({statut}) : {detail}"
    return f"Erreur Ollama: {exception}"


def call_ollama(prompt: str, temperature: float | None = None) -> tuple[str, int]:
    """
    Appelle l'API locale Ollama et retourne (texte_genere, tokens_utilises).
    Lève RuntimeError si Ollama est injoignable ou renvoie une erreur,
    pour que la route puisse la transformer proprement en réponse HTTP.

    Le modèle, la fenêtre de contexte et le délai de connexion viennent de la
    configuration : ils dépendent de la machine d'exécution, pas du code.
    """
    base_url = current_app.config["OLLAMA_URL"]
    model = current_app.config["OLLAMA_MODEL"]
    if temperature is None:
        temperature = TEMPERATURE_PAR_DEFAUT

    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    # Transmise explicitement : voir OLLAMA_NUM_CTX dans
                    # config.py — sans elle, Ollama tronque sans rien dire.
                    "num_ctx": current_app.config["OLLAMA_NUM_CTX"],
                },
            },
            # Couple (connexion, lecture). La lecture est volontairement
            # SANS limite : sur processeur seul, une reformulation de quelques
            # milliers de caractères dépasse la minute, et l'interrompre
            # affichait une erreur alors que la génération aboutissait. La
            # connexion, elle, garde un délai court pour qu'un Ollama non
            # lancé échoue tout de suite. Voir OLLAMA_CONNECT_TIMEOUT.
            timeout=(current_app.config["OLLAMA_CONNECT_TIMEOUT"], None),
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        # ConnectTimeout hérite de ConnectionError et tombe donc ici : un
        # délai de connexion dépassé veut dire la même chose qu'un refus de
        # connexion — Ollama n'est pas joignable à cette adresse.
        raise RuntimeError(
            f"Impossible de joindre Ollama sur {base_url}. "
            "Vérifiez qu'il est lancé sur votre machine."
        )
    except requests.exceptions.Timeout:
        # Filet de sécurité. Plus aucun délai n'est imposé à la lecture, donc
        # ce cas ne devrait plus se produire ; il reste traité pour qu'une
        # bibliothèque qui en lèverait un quand même donne une réponse 502
        # explicite au lieu d'une erreur 500 non interprétée.
        raise RuntimeError(
            f"La connexion à Ollama sur {base_url} n'a pas abouti. "
            "Vérifiez qu'il est lancé sur votre machine."
        )
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(_erreur_http(e, model))

    
    data = response.json()
    generated_text = data.get("response", "").strip()
    tokens_used = data.get("prompt_eval_count", 0) + data.get("eval_count",0)
    return generated_text, tokens_used