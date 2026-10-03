import json

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

# Consigne de prompt qui désactive le raisonnement sur les modèles qwen3.
#
# POURQUOI DEUX MÉCANISMES PLUTÔT QU'UN
#
# Le champ `think` de l'API ne fonctionne qu'à partir d'Ollama 0.9. Avant,
# c'est un champ inconnu : Ollama l'ignore SANS RIEN DIRE, le modèle raisonne
# quand même, et le bloc <think>...</think> arrive mélangé au texte de la
# réponse — c'est seulement depuis la 0.9 qu'il est renvoyé à part.
#
# Cette consigne, elle, voyage dans le prompt : elle marche sur toutes les
# versions. Les deux sont donc envoyées ensemble, et _nettoyer_raisonnement
# rattrape ce qui passerait malgré tout.
DIRECTIVE_SANS_RAISONNEMENT = "/no_think"


def _modele_qwen(model: str) -> bool:
    """
    La consigne /no_think est propre à qwen. Sur llama3.1 ou mistral, ce
    serait du texte parasite au milieu du prompt, que le modèle pourrait
    recopier dans sa réponse.
    """
    return "qwen" in model.lower()


def _nettoyer_raisonnement(texte: str) -> str:
    """
    Retire le bloc de raisonnement que certains modèles placent devant leur
    réponse.

    FILET DE SÉCURITÉ, ET IL A SERVI. Sur une version d'Ollama antérieure à
    la 0.9, ni le champ `think` ni la consigne de prompt ne garantissent
    l'absence du bloc, et celui-ci arrive alors collé au texte utile. Sans ce
    nettoyage, l'application proposait à l'utilisateur d'insérer dans son
    document plusieurs pages de monologue du modèle.

    On coupe après le DERNIER </think> : un modèle peut en émettre plusieurs,
    et c'est toujours ce qui suit le dernier qui constitue la réponse.
    """
    if "</think>" in texte:
        return texte.rsplit("</think>", 1)[1].strip()

    # Bloc ouvert mais jamais refermé : la génération s'est arrêtée au milieu
    # du raisonnement. Tout ce qu'on a est du raisonnement, il n'y a pas de
    # réponse à en tirer.
    if "<think>" in texte:
        return ""

    return texte.strip()


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


def _erreur_http(exception, model: str, detail: str | None = None) -> str:
    """
    Construit un message exploitable à partir d'une réponse HTTP en erreur.

    `detail` peut être fourni déjà lu. C'est indispensable sur une réponse
    obtenue en flux : une fois la connexion libérée, le corps n'est plus
    lisible, et le diagnostic d'Ollama serait perdu.
    """
    response = getattr(exception, "response", None)
    if detail is None:
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

class _ThinkRefuse(Exception):
    """
    Ollama a rejeté le champ `think` parce que le modèle n'a pas de mode
    raisonnement. Interne au module : convertie en nouvel essai, jamais
    remontée à l'appelant.
    """


def _charge_utile(
    model: str,
    prompt: str,
    temperature: float,
    num_ctx: int,
    think: bool | None,
) -> dict:
    """Corps de la requête envoyée à /api/generate."""
    charge = {
        "model": model,
        "prompt": prompt,
        # Flux NDJSON : une ligne JSON par jeton, et non un seul objet en fin
        # de génération. Voir _lire_flux pour la raison.
        "stream": True,
        "options": {
            "temperature": temperature,
            # Transmise explicitement : voir OLLAMA_NUM_CTX dans
            # config.py — sans elle, Ollama tronque sans rien dire.
            "num_ctx": num_ctx,
        },
    }
    # Champ de PREMIER niveau, pas une option : c'est ce qu'attend l'API
    # d'Ollama. Omis quand la configuration ne dit rien, pour ne pas imposer
    # un champ que les versions anciennes d'Ollama ignorent.
    if think is not None:
        charge["think"] = think
    return charge


def _lire_flux(response) -> tuple[str, int]:
    """
    Reconstitue le texte complet à partir du flux NDJSON d'Ollama.

    POURQUOI CETTE FONCTION EXISTE

    Avec `"stream": true`, Ollama ne renvoie PAS un objet JSON mais une ligne
    JSON par jeton généré :

        {"response":"Bon","done":false}
        {"response":"jour","done":false}
        {"response":"","done":true,"prompt_eval_count":30,"eval_count":12}

    `response.json()` échoue dessus — « Extra data: line 2 column 1 » — et
    l'échec se produisait APRÈS le bloc de traduction des erreurs, donc la
    route renvoyait un 500 opaque au lieu d'un 502 explicite. Toute génération
    était cassée.

    Les compteurs de jetons ne figurent que sur la dernière ligne, celle qui
    porte `done: true` : c'est elle, et elle seule, qui les donne.
    """
    morceaux: list[str] = []
    jetons = 0

    for ligne in response.iter_lines():
        if not ligne:
            continue
        try:
            # json.loads accepte les octets et suppose UTF-8, ce qui est ce
            # qu'Ollama envoie. On évite ainsi la question de l'encodage
            # déclaré, qu'Ollama ne précise pas toujours.
            bloc = json.loads(ligne)
        except ValueError:
            raise RuntimeError(
                "Réponse illisible d'Ollama : le flux ne contient pas du JSON "
                "ligne par ligne. Vérifiez la version d'Ollama."
            )

        # Une erreur peut arriver EN COURS de flux, après un statut 200 :
        # raise_for_status() ne la verra jamais.
        detail = bloc.get("error")
        if detail:
            raise RuntimeError(
                f"Erreur Ollama pendant la génération : "
                f"{' '.join(str(detail).split())[:200]}"
            )

        morceaux.append(bloc.get("response", ""))

        if bloc.get("done"):
            jetons = bloc.get("prompt_eval_count", 0) + bloc.get("eval_count", 0)

    return _nettoyer_raisonnement("".join(morceaux)), jetons


def _appel(base_url: str, charge: dict, connect_timeout: int) -> tuple[str, int]:
    """Un aller-retour avec Ollama, erreurs réseau traduites en RuntimeError."""
    model = charge["model"]
    try:
        # stream=True côté requests aussi : sans lui, la bibliothèque
        # accumulerait tout le corps avant de nous le rendre, ce qui annulerait
        # l'intérêt du flux.
        with requests.post(
            f"{base_url}/api/generate",
            json=charge,
            stream=True,
            # Couple (connexion, lecture). La lecture est volontairement
            # SANS limite : sur processeur seul, une reformulation de quelques
            # milliers de caractères dépasse la minute, et l'interrompre
            # affichait une erreur alors que la génération aboutissait. La
            # connexion, elle, garde un délai court pour qu'un Ollama non
            # lancé échoue tout de suite. Voir OLLAMA_CONNECT_TIMEOUT.
            timeout=(connect_timeout, None),
        ) as response:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                # Le corps est lu ICI, avant de quitter le bloc `with`.
                #
                # Avec stream=True, sortir du bloc libère la connexion et le
                # corps devient illisible : _detail_ollama renvoyait alors une
                # chaîne vide, et le diagnostic d'Ollama — « model not found »,
                # « does not support thinking » — était perdu au profit d'un
                # « 400 Client Error » sans information.
                #
                # Un test unitaire ne voyait pas le problème : son double de
                # réponse répond toujours à json(). Il a fallu un vrai serveur
                # HTTP pour le mettre en évidence.
                detail = _detail_ollama(response)
                if _est_think_refuse(e, detail):
                    raise _ThinkRefuse()
                raise RuntimeError(_erreur_http(e, model, detail))
            return _lire_flux(response)
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
        if _est_think_refuse(e):
            raise _ThinkRefuse()
        raise RuntimeError(_erreur_http(e, model))


def _est_think_refuse(exception, detail: str | None = None) -> bool:
    """
    Reconnaît le refus du champ `think` par Ollama.

    Ollama répond 400 « "<modèle>" does not support thinking » quand on lui
    passe `think` pour un modèle qui n'a pas de mode raisonnement. Le modèle
    venant de la configuration, la machine qui exécute le projet peut très bien
    tourner sur llama3.1 là où une autre tourne sur qwen3 : le code doit
    accepter les deux sans réglage.
    """
    response = getattr(exception, "response", None)
    if getattr(response, "status_code", None) != 400:
        return False
    if detail is None:
        detail = _detail_ollama(response)
    return "does not support thinking" in detail.lower()


def call_ollama(prompt: str, temperature: float | None = None) -> tuple[str, int]:
    """
    Appelle l'API locale Ollama et retourne (texte_genere, tokens_utilises).
    Lève RuntimeError si Ollama est injoignable ou renvoie une erreur,
    pour que la route puisse la transformer proprement en réponse HTTP.

    Le modèle, la fenêtre de contexte, le délai de connexion et le mode
    raisonnement viennent de la configuration : ils dépendent de la machine
    d'exécution, pas du code.
    """
    base_url = current_app.config["OLLAMA_URL"]
    model = current_app.config["OLLAMA_MODEL"]
    num_ctx = current_app.config["OLLAMA_NUM_CTX"]
    connect_timeout = current_app.config["OLLAMA_CONNECT_TIMEOUT"]
    think = current_app.config["OLLAMA_THINK"]
    if temperature is None:
        temperature = TEMPERATURE_PAR_DEFAUT

    # La consigne de prompt double le champ `think` de l'API, qui ne marche
    # qu'à partir d'Ollama 0.9 et est ignoré en silence avant.
    if not think and _modele_qwen(model):
        prompt = f"{DIRECTIVE_SANS_RAISONNEMENT}{prompt}\n\n"

    charge = _charge_utile(model, prompt, temperature, num_ctx, think)
    try:
        return _appel(base_url, charge, connect_timeout)
    except _ThinkRefuse:
        # Le modèle n'a pas de mode raisonnement : il n'y a rien à désactiver.
        # On refait l'appel sans le champ plutôt que de remonter une erreur
        # que l'utilisateur ne peut pas corriger lui-même.
        del charge["think"]
        try:
            return _appel(base_url, charge, connect_timeout)
        except _ThinkRefuse:
            # Ne devrait pas arriver : le champ a été retiré. Traduit quand
            # même, pour qu'une exception interne au module ne puisse jamais
            # remonter jusqu'à la route et s'y transformer en 500 opaque.
            raise RuntimeError(
                f"Ollama refuse le mode raisonnement pour « {model} » alors "
                "que le champ n'est plus envoyé. Vérifiez la version d'Ollama."
            )
