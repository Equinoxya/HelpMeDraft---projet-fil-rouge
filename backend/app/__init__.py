from flask import Flask, jsonify
from flask_cors import CORS

from app.extension import limiter, mail

from .config import Config
from .routes.admin_route import admin_bp
from .routes.auth_routes import auth_bp
from .routes.document_route import document_bp
from .routes.dossier_route import dossier_bp
from .routes.ia_route import ia_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Les origines viennent de la configuration : en conteneur, le frontend
    # n'est pas servi par Vite sur le port 5173. Voir CORS_ORIGINS dans config.py.
    CORS(app, supports_credentials=True, origins=app.config["CORS_ORIGINS"])
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
