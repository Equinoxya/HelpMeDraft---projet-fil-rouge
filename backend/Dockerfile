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

# Bibliothèques système de WeasyPrint, utilisé pour l'export PDF des documents
# terminés. Ce ne sont PAS des dépendances facultatives : la roue Python ne
# contient que les liaisons, et « import weasyprint » échoue sans elles — au
# démarrage de l'application, donc sur tous les points d'entrée à la fois, et
# non seulement sur la route d'export.
#
#   libpango-1.0-0, libpangoft2-1.0-0  mise en page et rendu du texte
#   libharfbuzz0b                      façonnage des glyphes
#   libharfbuzz-subset0                sous-ensemble des polices embarquées
#                                      dans le PDF. Sans elle, WeasyPrint
#                                      bascule sur fontTools et avertit que ce
#                                      repli disparaîtra dans une version
#                                      future : l'export cesserait alors de
#                                      fonctionner à la première mise à jour
#   libgdk-pixbuf-2.0-0                images référencées dans un document
#   libffi8                            appel des bibliothèques ci-dessus
#   fonts-dejavu-core                  une police À CHASSE FIXE pour les blocs
#                                      de code. L'image slim n'embarque aucune
#                                      police : sans elle, le texte sort dans
#                                      une police de secours, voire en carrés.
#
# --no-install-recommends et la purge des listes d'apt : une image qui porte
# son cache de paquets pèse une centaine de mégaoctets de plus sans rien
# apporter à l'exécution.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz0b \
        libharfbuzz-subset0 \
        libgdk-pixbuf-2.0-0 \
        libffi8 \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Les dépendances sont copiées et installées AVANT le code applicatif : Docker
# met en cache chaque étape, et le code change bien plus souvent que les
# dépendances. Inverser les deux lignes relancerait un pip install complet à
# chaque modification d'une route.
COPY requirements.lock .
# Trois protections contre une compromission de la chaîne d'approvisionnement,
# signalées par SonarCloud (docker:S8541 et S8544) :
#
#   --require-hashes      chaque paquet doit correspondre à l'empreinte inscrite
#                         dans le verrou. Un paquet altéré sur l'index est
#                         refusé, au lieu d'être installé en silence.
#   --only-binary :all:   n'installe que des roues précompilées. Une archive
#                         source exécute son setup.py PENDANT l'installation,
#                         c'est-à-dire du code arbitraire au moment du build.
#   requirements.lock     verrouille aussi les dépendances TRANSITIVES, ce que
#                         requirements.txt ne faisait pas (ticket KAN-102).
RUN pip install --no-cache-dir --require-hashes --only-binary :all: \
        -r requirements.lock

# Copie EXPLICITE, et non « COPY . . » (docker:S6470, critique). Une copie
# récursive embarque tout ce qui traîne dans le contexte — un .env oublié, une
# base locale, des clés — et le .dockerignore ne protège que de ce qu'on a
# pensé à y écrire. Nommer ce qu'on veut est plus sûr que nommer ce qu'on
# refuse.
COPY app/ ./app/
COPY database/ ./database/
COPY run.py utilitaires.py ./

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
