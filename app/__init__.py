from flask import Flask
import logging

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config


# -------------------------
# LOGGING
# -------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


# -------------------------
# EXTENSIONS
# -------------------------

limiter = Limiter(key_func=get_remote_address)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "https://med-dispense-theta.vercel.app"
            ]
        }
    })


    # -------------------------
    # INIT EXTENSIONS
    # -------------------------
    limiter.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # -------------------------
    # IMPORT MODELS
    # -------------------------
    from app import models

    # -------------------------
    # REGISTER BLUEPRINTS
    # -------------------------
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

    # -------------------------
    # HEALTH CHECK
    # -------------------------
    @app.route("/")
    def home():
        return {
            "status": "running",
            "message": "MED-DISPENSE API is live"
        }, 200

    return app