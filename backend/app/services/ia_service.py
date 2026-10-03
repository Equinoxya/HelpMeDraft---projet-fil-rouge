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


def call_ollama(prompt: str, temperature: float | None = None) -> tuple[str, int]:
    """
    Appelle l'API locale Ollama et retourne (texte_genere, tokens_utilises).
    Lève RuntimeError si Ollama est injoignable ou renvoie une erreur,
    pour que la route puisse la transformer proprement en réponse HTTP.

    Le modèle, la fenêtre de contexte et le délai maximum viennent de la
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
                "stream": False,
                "options": {
                    "temperature": temperature,
                    # Transmise explicitement : voir OLLAMA_NUM_CTX dans
                    # config.py — sans elle, Ollama tronque sans rien dire.
                    "num_ctx": current_app.config["OLLAMA_NUM_CTX"],
                },
            },
            timeout=current_app.config["OLLAMA_TIMEOUT"],
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Impossible de joindre Ollama sur {base_url}. Vérifié qu'il est lancé sur votre machine."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama a mis trop de temps à répondre")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Erreur Ollama: {e}")
    
    data = response.json()
    generated_text = data.get("response", "").strip()
    tokens_used = data.get("prompt_eval_count", 0) + data.get("eval_count",0)
    return generated_text, tokens_used