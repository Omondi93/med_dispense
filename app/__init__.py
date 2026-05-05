from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config["JWT_SECRET_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3NDI4MjYwMCwianRpIjoiZTBjOGE4MTMtOGRhNi00YzllLWFhMWYtMzNiMjU4ZjUzZDBmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzc0MjgyNjAwLCJjc3JmIjoiOGRiODkxZWUtM2VhYS00MTVkLThlNmUtY2UyZDQ4YzE1YjI5IiwiZXhwIjoxNzc0MjgzNTAwfQ.YsvBNZIIEGP_Sp4KQkIMRKTViHWcsR2wfrPuNsn6oNQ"

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models AFTER db is initialized
    from app import models
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.medicine import medicine_bp
    app.register_blueprint(medicine_bp)

    return app