from flask import Blueprint, request, jsonify, make_response, current_app
from flask_jwt_extended import set_access_cookies, jwt_required, get_jwt_identity

from app.services.auth_service import AuthenticationService
from app.services.user_service import UserService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/v1/register", methods=["POST"])
def register():
    content = request.json
    if not (
        "name" in content
        and "email" in content
        and "password" in content
        and "role" in content
    ):
        return jsonify({"error": "insufficient information provided"}), 400

    if not (
        isinstance(content["name"], str)
        and isinstance(content["email"], str)
        and isinstance(content["password"], str)
        and isinstance(content["role"], str)
    ):
        return jsonify({"error": "wrong types provided"}), 400

    result = UserService.register_user(
        content["email"], content["name"], content["password"], content["role"]
    )
    if result.ok:
        return (
            jsonify(
                {"result": "user registered", "user_id": result.data.get("user_id")}
            ),
            result.status_code or 201,
        )
    return jsonify({"error": result.error}), result.status_code or 400


@auth_bp.route("/api/v1/self", methods=["GET"])
@jwt_required()
def get_self():
    current_user_id = get_jwt_identity()
    res = UserService.get_user_info_by_id(current_user_id)
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 404
    return jsonify({"user": res.data}), 200


@auth_bp.route("/api/v1/login", methods=["POST"])
def login():
    content = request.json
    if not ("email" in content and "password" in content):
        return jsonify({"error": "insufficient information"}), 400
    if not (isinstance(content["email"], str) and isinstance(content["password"], str)):
        return jsonify({"error": "wrong types provided"}), 400

    auth_res = AuthenticationService.login_email_password(
        content["email"], content["password"]
    )
    if not auth_res.ok:
        return jsonify({"error": auth_res.error}), auth_res.status_code or 401

    user = auth_res.data
    token_res = AuthenticationService.generate_token(user.user_id)
    if not token_res.ok:
        return jsonify({"error": token_res.error}), token_res.status_code or 500

    token = token_res.data
    resp = jsonify({"result": "login success"})
    set_access_cookies(resp, token)
    return resp, 200
