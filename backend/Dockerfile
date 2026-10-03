# ==============================================================================
# HelpMeDraft — image du backend Flask
# ==============================================================================

FROM python:3.11-slim AS base

# Python en conteneur : pas de fichiers .pyc à écrire, et sortie non tamponnée
# pour que les journaux apparaissent immédiatement dans « docker compose logs »
# au lieu d'être retenus jusqu'à ce que le tampon se remplisse.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Les dépendances sont copiées et installées AVANT le code applicatif : Docker
# met en cache chaque étape, et le code change bien plus souvent que les
# dépendances. Inverser les deux lignes relancerait un pip install complet à
# chaque modification d'une route.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# L'application ne tourne pas en root. Un conteneur compromis hérite sinon de
# tous les droits sur son système de fichiers.
RUN useradd --create-home --uid 10001 helpmedraft \
    && chown -R helpmedraft:helpmedraft /app
USER helpmedraft

EXPOSE 5000

# Gunicorn plutôt que le serveur de développement de Flask, qui est
# mono-processus et le dit lui-même à chaque démarrage.
#
# --timeout 600 n'est pas un réglage de confort : l'appel à Ollama n'impose
# volontairement aucun délai de lecture (voir OLLAMA_CONNECT_TIMEOUT dans
# app/config.py), parce qu'un délai coupait des générations qui aboutissaient.
# Le délai par défaut de gunicorn est de 30 secondes : il tuerait le worker en
# pleine inférence, et l'utilisateur verrait une erreur réseau sans explication.
#
# --workers 2 : la limitation de débit (Flask-Limiter) compte en MÉMOIRE, donc
# par worker. Avec N workers, les seuils de /auth/login sont multipliés par N.
# Deux est un compromis assumé ; passer à un stockage Redis partagé est la vraie
# correction, et figure dans la TODO.
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--timeout", "600", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "run:app"]
