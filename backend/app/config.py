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
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
