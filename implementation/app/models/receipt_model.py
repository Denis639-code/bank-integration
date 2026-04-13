from app.shared import db
from sqlalchemy import Column, String, Float, DateTime, Integer
import datetime
import uuid


class Receipt(db.Model):
    def to_dict(self):
        return {
            "receipt_id": self.receipt_id,
            "user_id": self.user_id,
            "status": self.status,
            "amount": self.amount,
            "timestamp": int(self.timestamp.timestamp()),
        }

    __tablename__ = "receipts"

    receipt_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False)
    status = Column(String(20), nullable=False)
    amount = Column(Integer(), nullable=False)
    timestamp = Column(DateTime, default=lambda func: datetime.datetime.now(datetime.UTC), nullable=False)

    @classmethod
    def create_receipt(
        cls, user_id: str, status: str, amount: int, timestamp: datetime = None
    ):
        receipt_id = str(uuid.uuid4())
        ts = timestamp if timestamp else datetime.datetime.now(datetime.UTC)
        receipt = cls(
            receipt_id=receipt_id,
            user_id=user_id,
            status=status,
            amount=amount,
            timestamp=ts,
        )
        db.session.add(receipt)
        db.session.commit()
        return receipt

    @staticmethod
    def get_receipt_from_id(receipt_id: str):
        return Receipt.query.filter_by(receipt_id=receipt_id).first()

    @staticmethod
    def get_receipts():
        return Receipt.query.all()

    @staticmethod
    def get_receipts_of_user(user_id: str):
        return Receipt.query.filter_by(user_id=user_id).all()

    @staticmethod
    def update_receipt(
        receipt_id: str,
        status: str = None,
        amount: int = None,
        timestamp: datetime = None,
    ):
        receipt = Receipt.get_receipt_from_id(receipt_id)
        if not receipt:
            return False

        if status:
            receipt.status = status
        if amount is not None:
            receipt.amount = amount
        if timestamp:
            receipt.timestamp = timestamp

        db.session.commit()
        return True

    @staticmethod
    def delete_receipt(receipt_id: str):
        receipt = Receipt.get_receipt_from_id(receipt_id)
        if not receipt:
            return False

        db.session.delete(receipt)
        db.session.commit()
        return True
