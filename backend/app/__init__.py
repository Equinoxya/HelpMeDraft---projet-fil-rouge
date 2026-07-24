from flask import Flask
from .config import Config
from flask_cors import CORS
from .routes.auth_routes import auth_bp
from app.extension import mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
    mail.init_app(app)
    app.register_blueprint(auth_bp)
    return app