import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SÉCURITÉ : aucune valeur de repli. Une clé de secours en dur dans le code
    # source permettrait à l'application de démarrer sans .env avec une clé
    # connue de quiconque lit le dépôt : n'importe qui pourrait alors forger un
    # access token valide pour n'importe quel user_id (usurpation d'identité).
    # On préfère un échec bruyant au démarrage à un démarrage silencieusement
    # vulnérable (« fail fast, fail loud »).
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY est absente de l'environnement. "
            "Copier .env.example en backend/.env puis générer une clé : "
            'python -c "import secrets; print(secrets.token_urlsafe(64))"'
        )

    # Clé de session Flask. Distincte de JWT_SECRET_KEY : réutiliser une même
    # clé pour deux usages cryptographiques différents fait qu'une fuite sur
    # l'un compromet l'autre (séparation des clés). Flask s'en sert pour signer
    # les cookies de session et les messages flash. L'application n'en utilise
    # aucun aujourd'hui, mais une clé absente ferait échouer silencieusement le
    # premier usage ajouté — on la exige au démarrage, comme JWT_SECRET_KEY.
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY est absente de l'environnement. "
            "Copier .env.example en backend/.env puis générer une clé : "
            'python -c "import secrets; print(secrets.token_urlsafe(64))"'
        )

    # Environnement d'exécution : pilote l'attribut Secure du cookie de refresh.
    # En dev le front tourne en http://localhost, un cookie Secure ne serait
    # jamais envoyé ; hors dev, Secure est obligatoire sinon le jeton peut
    # transiter en clair sur HTTP et être capté (OWASP A02:2021).
    APP_ENV = os.getenv("APP_ENV", "development")
    COOKIE_SECURE = APP_ENV != "development"
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 2525))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

    # qwen2.5:3b — et le critère de choix n'est PAS la taille, c'est l'absence
    # de mode raisonnement.
    #
    # Le projet doit tourner sans carte graphique, où la vitesse est bornée par
    # la bande passante mémoire : à chaque jeton généré, le processeur relit
    # tous les poids. Un modèle plus petit est donc plus rapide. Mais ce facteur
    # est secondaire devant le NOMBRE de jetons produits, et c'est là que qwen3
    # a échoué.
    #
    # Mesuré sur la même machine, pour corriger « BJR je serai en retar » :
    #
    #              jetons générés   débit        durée
    #   qwen3:4b         1 443      11,9 j/s    2 min 01 s
    #   qwen2.5:3b           9      38,5 j/s       0,27 s
    #
    # qwen3 est un modèle à raisonnement : il produit un monologue d'analyse
    # avant de répondre, de taille à peu près constante — il « réfléchit »
    # autant pour une faute d'orthographe que pour trois pages. Ni le champ
    # `think` de l'API ni la consigne /no_think ne l'ont arrêté sur Ollama
    # 0.35.1. Le facteur 440 ci-dessus ne vient donc pas du matériel mais du
    # travail demandé.
    #
    # qwen2.5 est la génération précédente de la même famille : nativement
    # multilingue, ce qui compte pour une application de rédaction en français,
    # et sans mode raisonnement à neutraliser.
    #
    # LEÇON À RETENIR AVANT DE CHANGER CETTE VALEUR : pour de la réécriture,
    # un modèle à raisonnement est le mauvais outil, quelle que soit sa taille.
    # Vérifier qu'un modèle candidat n'en a pas avant de le retenir.
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

    # Fenêtre de contexte. SANS CETTE VALEUR, Ollama applique un défaut de 4096
    # jetons en deçà de 24 Gio de mémoire vidéo, et tronque SILENCIEUSEMENT
    # au-delà : aucune erreur, rien dans la réponse. La coupe se fait par
    # l'avant, donc ce sont les consignes du gabarit de prompt qui disparaissent
    # en premier, pas le texte de l'utilisateur. Le modèle reçoit alors un
    # document sans instruction, et répond n'importe quoi sans que rien ne le
    # signale.
    OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", 8192))

    # Mode « raisonnement » des modèles qui en ont un (qwen3, deepseek-r1...).
    #
    # DÉSACTIVÉ PAR DÉFAUT, et c'est le réglage qui change tout sur une machine
    # sans carte graphique. Un modèle à raisonnement produit d'abord un bloc
    # <think>...</think> avant sa réponse, et la taille de ce bloc est à peu
    # près CONSTANTE : il « réfléchit » autant pour corriger « BJR » que pour
    # reformuler trois pages. Mesuré sur qwen3:4b : plusieurs milliers de
    # jetons de réflexion, soit plusieurs minutes d'attente à 15 jetons par
    # seconde, pour corriger une phrase de quarante caractères.
    #
    # Ce mode n'apporte rien aux trois actions du projet — reformuler, corriger
    # et compléter sont des tâches de réécriture, pas de résolution de
    # problème. Le laisser actif, c'est payer un raisonnement dont la sortie
    # est jetée.
    #
    # Mettre OLLAMA_THINK=true seulement pour comparer les deux modes. Sur un
    # modèle sans mode raisonnement (llama3.1, mistral), Ollama rejette le
    # champ avec un 400 : ia_service refait alors l'appel sans lui, pour que la
    # même configuration marche sur les deux familles de modèles.
    OLLAMA_THINK = os.getenv("OLLAMA_THINK", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "oui",
    }

    # Délai maximum pour ÉTABLIR la connexion à Ollama, en secondes.
    #
    # Il n'y a volontairement PAS de délai sur la lecture de la réponse : une
    # inférence sur processeur seul peut dépasser la minute, et la couper
    # revient à jeter un texte qui était en train d'aboutir. L'utilisateur
    # voyait alors une erreur alors que rien n'avait échoué.
    #
    # Le délai de connexion, lui, reste court : si Ollama n'est pas lancé,
    # l'échec doit être immédiat et non après une attente inutile.
    OLLAMA_CONNECT_TIMEOUT = int(os.getenv("OLLAMA_CONNECT_TIMEOUT", 10))

    # Taille maximale du texte soumis à l'IA, en caractères.
    #
    # Cette borne n'est pas un garde-fou de sécurité : c'est la traduction d'une
    # contrainte matérielle. Reformuler produit à peu près autant de texte qu'il
    # en reçoit, donc le temps d'attente croît avec la taille du texte envoyé.
    # Maintenant qu'aucun délai ne coupe l'inférence, le plafond ne borne plus
    # un échec technique mais une ATTENTE : à 15 jetons par seconde sur
    # processeur seul, 3 000 caractères représentent environ 750 jetons à
    # générer, soit à peu près 50 secondes. C'est le maximum qu'on estime
    # raisonnable de faire patienter devant un compteur.
    #
    # Le frontend calcule et affiche cette estimation avant de lancer l'appel
    # (voir frontend/src/utils/iaEstimation.ts) : l'attente est annoncée, pas
    # subie.
    #
    # La valeur se règle donc par machine, dans .env — voir les deux profils
    # documentés dans .env.example.
    IA_MAX_CONTENU_LENGTH = int(os.getenv("IA_MAX_CONTENU_LENGTH", 3000))
