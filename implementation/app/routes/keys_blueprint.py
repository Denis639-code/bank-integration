from flask import Blueprint, request, Response, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.services.apikey_service import APIKeyService
from app.services.service_result import Result

keys_bp = Blueprint("keys", __name__)


@keys_bp.route("/api/v1/keys/<key_id>", methods=["GET"])
@jwt_required()
def get_key_info(key_id):
    key_res = APIKeyService.get_key_info(key_id)
    if not key_res.ok:
        return jsonify({"error": key_res.error}), key_res.status_code or 404

    key_info = key_res.data
    user_id = key_info["user_id"]

    current_user_id = get_jwt_identity()
    current_info_res = UserService.get_user_info_by_id(current_user_id)
    if current_info_res.ok:
        current_info = current_info_res.data
        if not (current_user_id == user_id) and current_info.get("role") != "admin":
            return jsonify({"error": "forbidden"}), 403

    return jsonify({"key": key_info}), 200


@keys_bp.route("/api/v1/keys/<key_id>", methods=["DELETE"])
@jwt_required()
def remove_key(key_id):
    key_res = APIKeyService.get_key_info(key_id)
    if not key_res.ok:
        return jsonify({"error": key_res.error}), key_res.status_code or 404

    key_info = key_res.data
    user_id = key_info["user_id"]

    current_user_id = get_jwt_identity()
    current_info_res = UserService.get_user_info_by_id(current_user_id)
    if current_info_res.ok:
        current_info = current_info_res.data
        if not (current_user_id == user_id) and current_info.get("role") != "admin":
            return jsonify({"error": "forbidden"}), 403

    del_res = APIKeyService.delete_api_key(key_id)
    if not del_res.ok:
        return jsonify({"error": del_res.error}), del_res.status_code or 500
    return "", del_res.status_code or 200
