import requests
from flask import current_app

OLLAMA_TIMEOUT = 60

PROMPT_TEMPLATES = {
    "reformuler": (
        "Tu es un assistant de rédaction juridique et administrative. "
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
        "Tu es un assistant de rédaction juridique et administrative. "
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

def call_ollama(prompt: str, model: str = "llama3.1") -> tuple[str, int]:
    """
    Appelle l'API locale Ollama et retourne (texte_genere, tokens_utilises).
    Lève RuntimeError si Ollama est injoignable ou renvoie une erreur,
    pour que la route puisse la transformer proprement en réponse HTTP.
    """
    
    base_url = current_app.config["OLLAMA_URL"]
    model = current_app.config["OLLAMA_MODEL"]
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options":{
                    "temperature": 0.7
                }
                
            },
            timeout=OLLAMA_TIMEOUT
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