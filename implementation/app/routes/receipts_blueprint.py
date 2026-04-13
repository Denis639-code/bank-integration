from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.receipt_service import ReceiptService


receipts_bp = Blueprint("receipts", __name__)


@receipts_bp.route("/api/v1/receipts", methods=["GET"])
def list_receipts():
    status = request.args.get("status")
    if status:
        res = ReceiptService.get_status_receipts(status)
    else:
        res = ReceiptService.get_receipts()

    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 500
    return jsonify({"receipts": res.data}), res.status_code or 200


@receipts_bp.route("/api/v1/receipts", methods=["POST"])
@jwt_required()
def create_receipt():
    content = request.json or {}
    user_id = get_jwt_identity()
    amount = content.get("amount")

    if not amount or not isinstance(amount, int) or amount <= 0:
        return jsonify({"error": "invalid amount"}), 400

    res = ReceiptService.create_receipt(user_id, amount)
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 500

    return (
        jsonify({"receipt": res.data}),
        res.status_code or 201
    )


@receipts_bp.route("/api/v1/users/<user_id>/receipts", methods=["GET"])
@jwt_required()
def receipts_of_user(user_id: str):
    res = ReceiptService.get_receipts()
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 500

    all_receipts = res.data
    user_receipts = [r for r in all_receipts if r.get("user_id") == user_id]
    return jsonify({"receipts": user_receipts}), 200


@receipts_bp.route("/api/v1/receipts/<receipt_id>", methods=["GET"])
def get_receipt(receipt_id: str):
    res = ReceiptService.get_receipts()
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 500

    all_receipts = res.data
    found = next((r for r in all_receipts if r.get("receipt_id") == receipt_id), None)
    if not found:
        return jsonify({"error": "receipt not found"}), 404
    return jsonify({"receipt": found}), 200


@receipts_bp.route("/api/v1/receipts/<receipt_id>", methods=["DELETE"])
@jwt_required()
def delete_receipt(receipt_id: str):
    res = ReceiptService.delete_receipt(receipt_id)
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 500
    return "", res.status_code or 200


@receipts_bp.route("/api/v1/receipts/<receipt_id>/reject", methods=["POST"])
@jwt_required()
def receipt_reject(receipt_id: str):
    user_id = get_jwt_identity()
    res = ReceiptService.reject_receipt(receipt_id, user_id)
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 400
    return jsonify({"result": "rejected"}), res.status_code or 200


@receipts_bp.route("/api/v1/receipts/<receipt_id>/approve", methods=["POST"])
@jwt_required()
def receipt_approve(receipt_id: str):
    user_id = get_jwt_identity()
    res = ReceiptService.approve_receipt(receipt_id, user_id)
    if not res.ok:
        return jsonify({"error": res.error}), res.status_code or 400
    return jsonify({"result": "approved"}), res.status_code or 200
