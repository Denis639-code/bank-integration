import re
from app.models.user_model import User
from app.shared import bcrypt
from .service_result import success, failure, Result


class UserService:
    def register_user(email: str, name: str, password: str, role: str) -> Result:
        if not re.match(r"^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}$", email):
            return failure("invalid email", 400)

        if User.get_user_by_email(email):
            return failure("email already exists", 400)

        if role not in ["salesman", "accountant", "manager", "admin"]:
            return failure("invalid role", 400)

        user = User.create_user(email=email, name=name, password=password, role=role)
        return success({"user_id": user.user_id}, 201)

    def get_userid_by_email(email: str) -> Result:
        user = User.get_user_by_email(email)
        if not user:
            return failure("user does not exist", 404)

        return success(user.user_id, 200)

    def delete_user_by_id(user_id: str) -> Result:
        if not User.get_user_by_id(user_id):
            return failure("user does not exist", 404)

        ok = User.delete_user(user_id)
        if not ok:
            return failure("failed deleting user", 500)
        return success(None, 200)

    def update_user_info(user_id: str, name: str, password: str, role: str) -> Result:
        if not User.get_user_by_id(user_id):
            return failure("user does not exist", 404)

        ok = User.update_user(user_id, name, password, role)
        if not ok:
            return failure("failed updating user", 500)
        return success(None, 200)

    def list_user_ids() -> Result:
        users = User.list_users()
        return success([user.user_id for user in users], 200)

    def get_user_info_by_id(user_id: str) -> Result:
        user = User.get_user_by_id(user_id)
        if not user:
            return failure("user not found", 404)
        return success({"user_id": user_id, "name": user.name, "email": user.email, "role": user.role}, 200)
