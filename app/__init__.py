from flask import Flask
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    limiter.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models AFTER db is initialized
    from app import models

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.medicine import medicine_bp
    app.register_blueprint(medicine_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.qrcode import qr_bp
    app.register_blueprint(qr_bp)

    from app.routes.batch import batch_bp
    app.register_blueprint(batch_bp)

    # ✅ FIXED INDENTATION
    @app.route("/")
    def home():
        return {
            "status": "running",
            "message": "MED-DISPENSE API is live"
        }, 200

    return app