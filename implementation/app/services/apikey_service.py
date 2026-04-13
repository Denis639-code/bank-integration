from app.models.apikey_model import APIKey
from flask import request, current_app, jsonify

from app.services.auth_service import AuthenticationService
from .service_result import success, failure, Result


def _replace_api_token():
    if "X-API-TOKEN" not in request.headers:
        return

    apikey_id = request.headers.get("X-API-TOKEN")
    token = APIKeyService.get_token_from_key(apikey_id)

    if token:
        request.environ["HTTP_AUTHORIZATION"] = "Bearer " + token


def register_api_hooks(app):
    app.before_request(_replace_api_token)


class APIKeyService:
    def create_api_key(user_id: str) -> Result:
        token_res = AuthenticationService.generate_token(user_id, is_expirable=False)
        if not token_res.ok:
            return failure("failed generating token", 500)

        token = token_res.data
        key = APIKey.create_api_key(user_id, token)
        if not key:
            return failure("failed creating api key", 500)

        return success(
            {
                "apikey_id": key.apikey_id,
                "user_id": key.user_id,
                "timestamp": int(key.timestamp.timestamp()),
            },
            201,
        )

    def get_token_from_key(apikey_id: str) -> str:
        key = APIKey.get_key_from_id(apikey_id)
        if not key:
            return None
        return key.token

    def delete_api_key(apikey_id: str) -> Result:
        ok = APIKey.delete_key(apikey_id)
        if not ok:
            return failure("failed deleting key", 500)
        return success(None, 200)

    def list_api_keys_of_user(user_id: str) -> Result:
        keys = APIKey.get_keys_of_user(user_id)
        if keys is None:
            return failure("failed fetching keys", 500)

        serialized = [
            {
                "apikey_id": key.apikey_id,
                "user_id": key.user_id,
                "timestamp": int(key.timestamp.timestamp()),
            }
            for key in keys
        ]
        return success(serialized, 200)

    def get_key_info(key_id: str) -> Result:
        key = APIKey.get_key_from_id(key_id)
        if not key:
            return failure("key not found", 404)
        return success(
            {
                "apikey_id": key.apikey_id,
                "user_id": key.user_id,
                "timestamp": int(key.timestamp.timestamp()),
            },
            200,
        )
