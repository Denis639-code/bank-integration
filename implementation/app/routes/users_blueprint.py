from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.services.apikey_service import APIKeyService
from app.services.service_result import Result

users_bp = Blueprint("users", __name__)


@users_bp.route("/api/v1/users", methods=["GET"])
@jwt_required()
def list_user_ids():
    res = UserService.list_user_ids()
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 500
    return jsonify({"user_ids": res.data}), res.status_code or 200


@users_bp.route("/api/v1/users/<user_id>", methods=["GET"])
@jwt_required()
def get_user_info(user_id):
    res = UserService.get_user_info_by_id(user_id)
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 404

    current_user_id = get_jwt_identity()
    current_info_res = UserService.get_user_info_by_id(current_user_id)
    if current_info_res.ok:
        current_info = current_info_res.data
        if current_info.get("role") == "salesman" and current_user_id != user_id:
            return jsonify({"error": "forbidden"}), 403

    return jsonify({"user": res.data}), 200


@users_bp.route("/api/v1/users/<user_id>", methods=["POST"])
@jwt_required()
def update_user_info(user_id):
    old_res = UserService.get_user_info_by_id(user_id)
    if not old_res.ok:
        return jsonify({"error": old_res.error}), old_res.status_code or 404

    current_user_id = get_jwt_identity()
    current_info_res = UserService.get_user_info_by_id(current_user_id)
    if current_info_res.ok:
        current_info = current_info_res.data
        if not (current_user_id == user_id) and current_info.get("role") != "admin":
            return jsonify({"error": "forbidden"}), 403

    content = request.json or {}
    name = content.get("name")
    password = content.get("password")
    role = content.get("role")

    res = UserService.update_user_info(user_id, name, password, role)
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 400
    return jsonify({"result": "success"}), res.status_code or 200


@users_bp.route("/api/v1/users/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    old_res = UserService.get_user_info_by_id(user_id)
    if not old_res.ok:
        return jsonify({"error": old_res.error}), old_res.status_code or 404

    current_user_id = get_jwt_identity()
    current_info_res = UserService.get_user_info_by_id(current_user_id)
    if current_info_res.ok:
        current_info = current_info_res.data
        if not (current_user_id == user_id) and current_info.get("role") != "admin":
            return jsonify({"error": "forbidden"}), 403

    res = UserService.delete_user_by_id(user_id)
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 500
    return "", res.status_code or 200


@users_bp.route("/api/v1/users/<user_id>/keys", methods=["GET"])
@jwt_required()
def fetch_api_keys(user_id):
    current_user_id = get_jwt_identity()
    current_info = UserService.get_user_info_by_id(current_user_id)
    if isinstance(current_info, Result):
        if not current_info.ok:
            return (
                jsonify({"error": current_info.error}),
                current_info.status_code or 500,
            )
        current_info = current_info.data

    if (user_id != current_user_id) and current_info.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403

    keys_res = APIKeyService.list_api_keys_of_user(user_id)
    if not keys_res.ok:
        return jsonify({"error": keys_res.error}), keys_res.status_code or 500

    return jsonify({"keys": keys_res.data}), keys_res.status_code or 200


@users_bp.route("/api/v1/users/<user_id>/keys", methods=["POST"])
@jwt_required()
def create_api_key(user_id):
    current_user_id = get_jwt_identity()
    current_info = UserService.get_user_info_by_id(current_user_id)
    if isinstance(current_info, Result):
        if not current_info.ok:
            return (
                jsonify({"error": current_info.error}),
                current_info.status_code or 500,
            )
        current_info = current_info.data

    if (user_id != current_user_id) and current_info.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403

    key_res = APIKeyService.create_api_key(user_id)
    if not key_res.ok:
        return jsonify({"error": key_res.error}), key_res.status_code or 500

    return jsonify({"apikey": key_res.data}), key_res.status_code or 201
