from app.models.user_model import User
from app.shared import jwt
from flask_jwt_extended import create_access_token
from flask import jsonify
from .service_result import success, failure, Result

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return jsonify({"error": "missing or invalid token"}), 401


class AuthenticationService:
    def login_email_password(email: str, password: str) -> Result:
        user = User.get_user_by_email(email)
        if user and user.check_password(password):
            return success(user, 200)
        return failure("invalid credentials", 401)

    def generate_token(user_id: str, is_expirable: int = True) -> Result:
        user = User.get_user_by_id(user_id)
        if not user:
            return failure("user not found", 404)

        if is_expirable:
            token = create_access_token(identity=user_id)
        else:
            token = create_access_token(identity=user_id, expires_delta=False)

        return success(token, 200)
