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

    # qwen3:4b plutôt qu'un modèle de 7 ou 8 milliards de paramètres : le projet
    # doit tourner sur une machine sans carte graphique, où la vitesse est bornée
    # par la bande passante mémoire — à chaque jeton généré, le processeur relit
    # tous les poids. Un modèle deux fois plus petit est donc deux fois plus
    # rapide, et qwen3 est nativement multilingue, ce qui compte pour une
    # application de rédaction en français.
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")

    # Fenêtre de contexte. SANS CETTE VALEUR, Ollama applique un défaut de 4096
    # jetons en deçà de 24 Gio de mémoire vidéo, et tronque SILENCIEUSEMENT
    # au-delà : aucune erreur, rien dans la réponse. La coupe se fait par
    # l'avant, donc ce sont les consignes du gabarit de prompt qui disparaissent
    # en premier, pas le texte de l'utilisateur. Le modèle reçoit alors un
    # document sans instruction, et répond n'importe quoi sans que rien ne le
    # signale.
    OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", 8192))

    # Délai maximum d'un appel d'inférence, en secondes.
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", 60))

    # Taille maximale du texte soumis à l'IA, en caractères.
    #
    # Cette borne n'est pas un garde-fou de sécurité : c'est la traduction d'une
    # contrainte matérielle. Reformuler produit à peu près autant de texte qu'il
    # en reçoit, donc le plafond réel est donné par ce que la machine peut
    # générer avant OLLAMA_TIMEOUT. À 15 jetons par seconde sur processeur seul,
    # 60 secondes donnent environ 900 jetons, soit à peu près 3 300 caractères ;
    # on retient 3 000 pour garder une marge. Promettre 20 000 caractères sur
    # une telle machine, c'est promettre un délai dépassé.
    #
    # La valeur se règle donc par machine, dans .env — voir les deux profils
    # documentés dans .env.example.
    IA_MAX_CONTENU_LENGTH = int(os.getenv("IA_MAX_CONTENU_LENGTH", 3000))
