import logging

from app import create_app

# Niveau INFO, sinon les journaux de l'application sont AVALÉS.
#
# Le journaliseur racine de Python est à WARNING par défaut : tout appel à
# logger.info() est donc jeté, sans que rien ne le dise. C'est ce qui est arrivé
# à la ligne « Origines autorisées (CORS) » de app/__init__.py — posée
# justement pour rendre diagnosticable une panne d'origine croisée, et invisible
# en pratique.
#
# Placé ici et non dans create_app() : configurer le journaliseur racine est une
# décision de l'exécutable, pas de la fabrique d'application. Sous gunicorn
# (voir le Dockerfile), c'est gunicorn qui s'en charge, et la fabrique ne doit
# pas lui marcher dessus.
#
# force=True parce que Flask installe son propre gestionnaire à l'import :
# sans lui, basicConfig constate qu'un gestionnaire existe déjà et ne fait rien.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    force=True,
)

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
