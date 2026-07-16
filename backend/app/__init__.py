from flask import Flask
from .config import Config
from flask_cors import CORS
from .routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
    app.register_blueprint(auth_bp)
    return app