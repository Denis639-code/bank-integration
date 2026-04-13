from app.shared import db, bcrypt
import uuid
from sqlalchemy import Column, String


class User(db.Model):
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
        }

    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True)
    email = Column(String(60), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False)
    name = Column(String(80), nullable=False)

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    @classmethod
    def create_user(cls, name: str, email: str, password: str, role: str):
        user_id = str(uuid.uuid4())
        user = cls(
            user_id=user_id,
            name=name,
            email=email,
            password=bcrypt.generate_password_hash(password).decode("utf-8"),
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id: str):
        return User.query.filter_by(user_id=user_id).first()

    @staticmethod
    def get_user_by_email(email: str):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def delete_user(user_id: str) -> bool:
        user = User.get_user_by_id(user_id)
        if not user:
            return False

        db.session.delete(user)
        db.session.commit()
        return True

    @staticmethod
    def update_user(user_id: str, name: str, password: str, role: str) -> bool:
        user = User.get_user_by_id(user_id)
        if not user:
            return False

        if name:
            user.name = name
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        if role:
            user.role = role

        db.session.commit()
        return True

    @staticmethod
    def list_users():
        return User.query.all()
