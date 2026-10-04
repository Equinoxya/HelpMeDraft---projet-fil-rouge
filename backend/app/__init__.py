import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

from app.extension import limiter, mail

from .config import Config
from .routes.admin_route import admin_bp
from .routes.auth_routes import auth_bp
from .routes.document_route import document_bp
from .routes.dossier_route import dossier_bp
from .routes.ia_route import ia_bp

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    origines = app.config["CORS_ORIGINS"]
    # Les origines viennent de la configuration : en conteneur, le frontend
    # n'est pas servi par Vite sur le port 5173. Voir CORS_ORIGINS dans config.py.
    CORS(app, supports_credentials=True, origins=origines)

    # ── Rendre un refus d'origine VISIBLE ────────────────────────────────────
    #
    # Une origine refusée est la panne la plus difficile à diagnostiquer de
    # cette application, parce qu'elle ne ressemble pas à une erreur : le
    # serveur répond 200 à la requête préalable, simplement sans l'en-tête
    # Access-Control-Allow-Origin. Côté serveur, rien. Côté navigateur, un
    # message de politique CORS, et des formulaires d'inscription et de
    # connexion qui échouent sans explication.
    #
    # C'est arrivé : CORS_ORIGINS valait « http://localhost:8080 », la valeur du
    # conteneur, dans le .env d'un poste lancé avec Vite sur 5173. Le journal
    # ci-dessous aurait donné la réponse en une ligne au lieu d'une enquête.
    logger.info("Origines autorisées (CORS) : %s", ", ".join(origines))

    @app.after_request
    def journaliser_origine_refusee(reponse):
        origine = request.headers.get("Origin")
        # On ne journalise que les requêtes qui PORTENT une origine : un appel
        # curl ou une sonde de santé n'en a pas, et n'est pas concerné par la
        # politique d'origine croisée. Sans ce filtre, le journal se remplirait
        # d'avertissements pour des requêtes parfaitement normales.
        if origine and origine not in origines:
            logger.warning(
                "Origine REFUSÉE : %s (%s %s). Les origines autorisées sont : %s. "
                "Le navigateur signalera « No 'Access-Control-Allow-Origin' header ». "
                "Corriger CORS_ORIGINS — http://localhost:5173 avec Vite, "
                "http://localhost:8080 en conteneur.",
                origine,
                request.method,
                request.path,
                ", ".join(origines),
            )
        return reponse

    mail.init_app(app)
    limiter.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(dossier_bp)
    app.register_blueprint(ia_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({"error": "Trop de tentatives, réessayer plus tard"}), 429

    return app
