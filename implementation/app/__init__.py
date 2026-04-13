import os
from flask import Flask, jsonify

from .shared import db, bcrypt, jwt


def create_app(test_config=None):
    app = Flask(
        __name__, template_folder="webui/templates", static_folder="webui/static"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_VERIFY_SUB"] = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from app.routes.auth_blueprint import auth_bp
    from app.routes.users_blueprint import users_bp
    from app.routes.keys_blueprint import keys_bp
    from app.routes.receipts_blueprint import receipts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(keys_bp)
    app.register_blueprint(receipts_bp)

    from app.services.apikey_service import register_api_hooks

    register_api_hooks(app)

    with app.app_context():
        db.create_all()

    return app
