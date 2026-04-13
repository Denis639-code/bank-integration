from app.models.receipt_model import Receipt
from app.models.user_model import User
from .service_result import success, failure, Result
import datetime

STATUS_LIST = ["created", "submitted", "approved_accountant", "approved_manager"]


class ReceiptService:
    @staticmethod
    def _convert_timestamp(timestamp: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def get_receipts() -> Result:
        receipts = Receipt.get_receipts()
        return success([r.to_dict() for r in receipts], 200)

    @staticmethod
    def get_status_receipts(status: str) -> Result:
        receipts = Receipt.get_receipts()
        filtered = [r for r in receipts if r.status == status]
        return success([r.to_dict() for r in filtered], 200)

    @staticmethod
    def create_receipt(user_id: str, amount: int, timestamp: int = None) -> Result:
        user = User.get_user_by_id(user_id)
        if not user:
            return failure("user not found", 404)

        if timestamp:
            ts = ReceiptService._convert_timestamp(timestamp)
        else:
            ts = datetime.datetime.now(datetime.UTC)

        receipt = Receipt.create_receipt(
            user_id=user_id, status="created", amount=amount, timestamp=ts
        )
        if not receipt:
            return failure("failed creating receipt", 500)
        return success(receipt.to_dict(), 201)

    @staticmethod
    def approve_receipt(receipt_id: str, user_id: str) -> Result:
        receipt = Receipt.get_receipt_from_id(receipt_id)
        if not receipt:
            return failure("receipt not found", 404)

        user = User.get_user_by_id(user_id)
        if not user:
            return failure("user not found", 404)

        current_status = receipt.status

        if current_status == "created":
            if receipt.user_id != user_id:
                return failure("only the receipt owner can submit", 403)
            ok = Receipt.update_receipt(receipt_id, status="submitted")
            if not ok:
                return failure("failed updating receipt", 500)
            return success(None, 200)

        elif current_status == "submitted":
            if user.role != "accountant":
                return failure("only accountants can approve at this stage", 403)
            if receipt.user_id == user_id:
                return failure("accountant cannot approve their own receipt", 403)
            ok = Receipt.update_receipt(receipt_id, status="approved_accountant")
            if not ok:
                return failure("failed updating receipt", 500)
            return success(None, 200)

        elif current_status == "approved_accountant":
            if user.role != "manager":
                return failure("only managers can approve at this stage", 403)
            if receipt.user_id == user_id:
                return failure("manager cannot approve their own receipt", 403)
            ok = Receipt.update_receipt(receipt_id, status="approved_manager")
            if not ok:
                return failure("failed updating receipt", 500)
            return success(None, 200)

        elif current_status == "approved_manager":
            return failure("receipt already fully approved", 400)

        else:
            return failure(f"cannot approve receipt in status {current_status}", 400)

    @staticmethod
    def reject_receipt(receipt_id: str, user_id: str) -> Result:
        receipt = Receipt.get_receipt_from_id(receipt_id)
        if not receipt:
            return failure("receipt not found", 404)

        user = User.get_user_by_id(user_id)
        if not user:
            return failure("user not found", 404)

        if user.role not in ["accountant", "manager"]:
            return failure("only accountants and managers can reject receipts", 403)

        if user.role == "accountant" and receipt.status != "submitted":
            return failure("accountants can only reject submitted receipts", 400)
        if user.role == "manager" and receipt.status != "approved_accountant":
            return failure(
                "managers can only reject receipts approved by accountant", 400
            )

        ok = Receipt.update_receipt(receipt_id, status="created")
        if not ok:
            return failure("failed updating receipt", 500)
        return success(None, 200)

    @staticmethod
    def delete_receipt(receipt_id: str) -> Result:
        ok = Receipt.delete_receipt(receipt_id)
        if not ok:
            return failure("failed deleting receipt", 500)
        return success(None, 200)
