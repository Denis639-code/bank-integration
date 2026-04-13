from app.shared import db
from sqlalchemy import Column, String, DateTime

import uuid
import datetime


class APIKey(db.Model):
    __tablename__ = "apikeys"

    apikey_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False)
    token = Column(String(400), nullable=False)
    timestamp = Column(DateTime(), nullable=False)

    @classmethod
    def create_api_key(cls, user_id: str, api_token: str):
        key_id = str(uuid.uuid4())
        key = cls(
            apikey_id=key_id,
            user_id=user_id,
            token=api_token,
            timestamp=datetime.datetime.now(),
        )
        db.session.add(key)
        db.session.commit()
        return key

    @staticmethod
    def get_key_from_id(key_id: str):
        return APIKey.query.filter_by(apikey_id=key_id).first()

    @staticmethod
    def get_keys_of_user(user_id: str):
        return APIKey.query.filter_by(user_id=user_id).all()

    @staticmethod
    def delete_key(key_id: str):
        key = APIKey.get_key_from_id(key_id)
        if not key:
            return False

        db.session.delete(key)
        db.session.commit()
        return True
