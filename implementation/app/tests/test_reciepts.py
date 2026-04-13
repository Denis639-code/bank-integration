import sys
import pytest
import string
import random


sys.path.append("../")

from app import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    return app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()



def _login(client, role = "salesman"):
    name = f"reciepts_test_user_{role}"
    email = name.lower() + "@example.com"
    password = "1234"
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": role
    })

    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200

def test_post_receipt(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount

def test_post_receipt_invalid_amount(client):
    _login(client)

    amount = -10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 400


def test_post_receipt_and_get_receipt(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount

    receipt_id = data["receipt_id"]

    response = client.get(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 200

    data = response.get_json()["receipt"]
    assert data["receipt_id"] == receipt_id
    assert data["amount"] == amount

def test_get_not_existing_receipt(client):
    _login(client)

    receipt_id = 1

    response = client.get(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 404


def test_post_receipt_and_get_receipts(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount

    receipt_id = data["receipt_id"]

    response = client.get("/api/v1/receipts")
    assert response.status_code == 200

    data = response.get_json()["receipts"]
    assert receipt_id in [receipt["receipt_id"] for receipt in data]

def test_post_receipts_and_get_receipts_with_filter(client):
    _login(client)

    amount_1 = 10
    response = client.post("/api/v1/receipts", json={'amount': amount_1})
    assert response.status_code == 201
    data = response.get_json()["receipt"]
    assert data["amount"] == amount_1
    receipt_id_1 = data["receipt_id"]

    amount_2 = 10
    response = client.post("/api/v1/receipts", json={'amount': amount_2})
    assert response.status_code == 201
    data = response.get_json()["receipt"]
    assert data["amount"] == amount_2
    receipt_id_2 = data["receipt_id"]

    response = client.post(f"/api/v1/receipts/{receipt_id_1}/approve")
    assert response.status_code == 200


    response = client.get("/api/v1/receipts?status=created")
    assert response.status_code == 200

    data = response.get_json()["receipts"]
    assert receipt_id_1 not in [receipt["receipt_id"] for receipt in data]
    assert receipt_id_2 in [receipt["receipt_id"] for receipt in data]

    response = client.get("/api/v1/receipts?status=submitted")
    assert response.status_code == 200

    data = response.get_json()["receipts"]
    assert receipt_id_1 in [receipt["receipt_id"] for receipt in data]
    assert receipt_id_2 not in [receipt["receipt_id"] for receipt in data]


def test_post_receipt_and_get_user_receipts(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount

    receipt_id = data["receipt_id"]

    response = client.get("/api/v1/self")
    assert response.status_code == 200
    data = response.get_json()
    assert "user" in data
    user_id = data["user"]["user_id"]

    response = client.get(f"/api/v1/users/{user_id}/receipts")
    assert response.status_code == 200

    data = response.get_json()["receipts"]
    assert receipt_id in [receipt["receipt_id"] for receipt in data]


def test_post_receipt_and_del_receipt(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount

    receipt_id = data["receipt_id"]

    response = client.delete(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 200

    response = client.get("/api/v1/receipts")
    assert response.status_code == 200

    data = response.get_json()["receipts"]
    assert receipt_id not in [receipt["receipt_id"] for receipt in data]

def test_del_not_existing_receipt(client):
    _login(client)

    receipt_id = 1

    response = client.delete(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 500

def test_post_receipt_and_approve_receipt(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount
    assert data["status"] == "created"

    receipt_id = data["receipt_id"]

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200

    response = client.get(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 200

    data = response.get_json()["receipt"]
    assert data["receipt_id"] == receipt_id
    assert data["amount"] == amount
    assert data["status"] == "submitted"

def test_post_receipt_and_reject_receipt(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount
    assert data["status"] == "created"

    receipt_id = data["receipt_id"]

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200

    _login(client, "accountant")

    response = client.post(f"/api/v1/receipts/{receipt_id}/reject")
    assert response.status_code == 200

    response = client.get(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 200

    data = response.get_json()["receipt"]
    assert data["receipt_id"] == receipt_id
    assert data["amount"] == amount
    assert data["status"] == "created"

def test_post_receipt_and_reject(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount
    assert data["status"] == "created"

    receipt_id = data["receipt_id"]

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200

    response = client.post(f"/api/v1/receipts/{receipt_id}/reject")
    assert response.status_code == 403


def test_post_receipt_and_approve_receipt_by_unauthorized_role(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount
    assert data["status"] == "created"

    receipt_id = data["receipt_id"]

    _login(client, "accountant")

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 403


def test_post_receipt_and_reject_receipt_by_unauthorized_role(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount
    assert data["status"] == "created"

    receipt_id = data["receipt_id"]

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200

    _login(client, "salesman")

    response = client.post(f"/api/v1/receipts/{receipt_id}/reject")
    assert response.status_code == 403

def test_post_receipt_with_invalid_amount_type(client):
    _login(client)

    amount = "invalid_amount"
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 400


def test_post_receipt_with_missing_amount_field(client):
    _login(client)

    response = client.post("/api/v1/receipts", json={})
    assert response.status_code == 400

def test_post_receipt_and_approve_already_approved_receipt(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount
    assert data["status"] == "created"

    receipt_id = data["receipt_id"]

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 403

def test_post_receipt_accountant_approving_own_receipt(client):
    _login(client, "accountant")

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount
    assert data["status"] == "created"

    receipt_id = data["receipt_id"]

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 403




def test_post_receipt_approve_fullflow(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount
    assert data["status"] == "created"

    receipt_id = data["receipt_id"]

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200

    response = client.get(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 200

    data = response.get_json()["receipt"]
    assert data["receipt_id"] == receipt_id
    assert data["amount"] == amount
    assert data["status"] == "submitted"

    _login(client, "accountant")

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200
    response = client.get(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 200
    data = response.get_json()["receipt"]
    assert data["receipt_id"] == receipt_id
    assert data["amount"] == amount
    assert data["status"] == "approved_accountant"

    _login(client, "manager")
    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200
    response = client.get(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 200
    data = response.get_json()["receipt"]
    assert data["receipt_id"] == receipt_id
    assert data["amount"] == amount
    assert data["status"] == "approved_manager"


def test_post_receipt_and_delete(client):
    _login(client)

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount

    receipt_id = data["receipt_id"]

    response = client.delete(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 200

    response = client.get(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 404

def test_post_receipt_and_delete_not_existing_receipt(client):
    _login(client)

    receipt_id = "non_existing_receipt_id"

    response = client.delete(f"/api/v1/receipts/{receipt_id}")
    assert response.status_code == 500

def test_post_receipt_and_manager_approving_own_receipt(client):
    _login(client, "manager")

    amount = 10
    response = client.post("/api/v1/receipts", json={'amount': amount})
    assert response.status_code == 201

    data = response.get_json()["receipt"]
    assert data["amount"] == amount
    assert data["status"] == "created"

    receipt_id = data["receipt_id"]

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 200

    response = client.post(f"/api/v1/receipts/{receipt_id}/approve")
    assert response.status_code == 403