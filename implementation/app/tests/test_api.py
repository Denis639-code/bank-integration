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


def _generate_name(length):
    letters = string.ascii_letters
    return random.choice(string.ascii_letters).upper() + ''.join(random.choice(letters) for i in range(length-1))

def _generate_password(length):
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for i in range(length))


def test_create_api_key_requires_auth(client):
    response = client.post("/api/v1/users/test-user-id/keys")
    assert response.status_code == 401


def test_user_can_create_own_api_key(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    role = "salesman"
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": role
    })
    assert response.status_code == 201
    user_id = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    response = client.post(f"/api/v1/users/{user_id}/keys")
    assert response.status_code == 201
    data = response.get_json()
    assert "apikey" in data
    assert data["apikey"]["apikey_id"]
    assert data["apikey"]["user_id"] == user_id


def test_salesman_cannot_create_api_key_for_other_user(client):
    name1 = _generate_name(10) + _generate_name(10)
    email1 = name1.lower() + "@example.com"
    password1 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name1,
        "email": email1,
        "password": password1,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id1 = response.get_json()["user_id"]
    
    name2 = _generate_name(10) + _generate_name(10)
    email2 = name2.lower() + "@example.com"
    password2 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name2,
        "email": email2,
        "password": password2,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id2 = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email1,
        "password": password1
    })
    assert response.status_code == 200
    
    response = client.post(f"/api/v1/users/{user_id2}/keys")
    assert response.status_code == 403


def test_admin_can_create_api_key_for_any_user(client):
    name1 = _generate_name(10) + _generate_name(10)
    email1 = name1.lower() + "@example.com"
    password1 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name1,
        "email": email1,
        "password": password1,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id1 = response.get_json()["user_id"]
    
    name2 = _generate_name(10) + _generate_name(10)
    email2 = name2.lower() + "@example.com"
    password2 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name2,
        "email": email2,
        "password": password2,
        "role": "admin"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email2,
        "password": password2
    })
    assert response.status_code == 200
    
    response = client.post(f"/api/v1/users/{user_id1}/keys")
    assert response.status_code == 201
    data = response.get_json()
    assert data["apikey"]["user_id"] == user_id1


def test_list_api_keys_requires_auth(client):
    response = client.get("/api/v1/users/test-user-id/keys")
    assert response.status_code == 401


def test_user_can_list_own_api_keys(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    client.post(f"/api/v1/users/{user_id}/keys")
    client.post(f"/api/v1/users/{user_id}/keys")
    
    response = client.get(f"/api/v1/users/{user_id}/keys")
    assert response.status_code == 200
    data = response.get_json()
    assert "keys" in data
    assert isinstance(data["keys"], list)
    assert len(data["keys"]) >= 2


def test_user_can_list_empty_api_keys(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    response = client.get(f"/api/v1/users/{user_id}/keys")
    assert response.status_code == 200
    data = response.get_json()
    assert data["keys"] == []


def test_salesman_cannot_list_other_user_api_keys(client):
    name1 = _generate_name(10) + _generate_name(10)
    email1 = name1.lower() + "@example.com"
    password1 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name1,
        "email": email1,
        "password": password1,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id1 = response.get_json()["user_id"]
    
    name2 = _generate_name(10) + _generate_name(10)
    email2 = name2.lower() + "@example.com"
    password2 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name2,
        "email": email2,
        "password": password2,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id2 = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email1,
        "password": password1
    })
    assert response.status_code == 200
    
    response = client.get(f"/api/v1/users/{user_id2}/keys")
    assert response.status_code == 403


def test_admin_can_list_any_user_api_keys(client):
    name1 = _generate_name(10) + _generate_name(10)
    email1 = name1.lower() + "@example.com"
    password1 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name1,
        "email": email1,
        "password": password1,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id1 = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email1,
        "password": password1
    })
    assert response.status_code == 200
    client.post(f"/api/v1/users/{user_id1}/keys")
    
    name2 = _generate_name(10) + _generate_name(10)
    email2 = name2.lower() + "@example.com"
    password2 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name2,
        "email": email2,
        "password": password2,
        "role": "admin"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email2,
        "password": password2
    })
    assert response.status_code == 200
    
    response = client.get(f"/api/v1/users/{user_id1}/keys")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["keys"]) >= 1


def test_get_api_key_info_requires_auth(client):
    response = client.get("/api/v1/keys/test-key-id")
    assert response.status_code == 401


def test_user_can_get_own_api_key_info(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    key_resp = client.post(f"/api/v1/users/{user_id}/keys")
    key_id = key_resp.get_json()["apikey"]["apikey_id"]
    
    response = client.get(f"/api/v1/keys/{key_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "key" in data
    assert data["key"]["apikey_id"] == key_id
    assert data["key"]["user_id"] == user_id


def test_salesman_cannot_get_other_user_api_key_info(client):
    name1 = _generate_name(10) + _generate_name(10)
    email1 = name1.lower() + "@example.com"
    password1 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name1,
        "email": email1,
        "password": password1,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id1 = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email1,
        "password": password1
    })
    assert response.status_code == 200
    key_resp = client.post(f"/api/v1/users/{user_id1}/keys")
    key_id = key_resp.get_json()["apikey"]["apikey_id"]
    
    name2 = _generate_name(10) + _generate_name(10)
    email2 = name2.lower() + "@example.com"
    password2 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name2,
        "email": email2,
        "password": password2,
        "role": "salesman"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email2,
        "password": password2
    })
    assert response.status_code == 200
    
    response = client.get(f"/api/v1/keys/{key_id}")
    assert response.status_code == 403


def test_admin_can_get_any_user_api_key_info(client):
    name1 = _generate_name(10) + _generate_name(10)
    email1 = name1.lower() + "@example.com"
    password1 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name1,
        "email": email1,
        "password": password1,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id1 = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email1,
        "password": password1
    })
    assert response.status_code == 200
    key_resp = client.post(f"/api/v1/users/{user_id1}/keys")
    key_id = key_resp.get_json()["apikey"]["apikey_id"]
    
    name2 = _generate_name(10) + _generate_name(10)
    email2 = name2.lower() + "@example.com"
    password2 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name2,
        "email": email2,
        "password": password2,
        "role": "admin"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email2,
        "password": password2
    })
    assert response.status_code == 200
    
    response = client.get(f"/api/v1/keys/{key_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["key"]["user_id"] == user_id1


def test_get_nonexistent_api_key(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "salesman"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    response = client.get("/api/v1/keys/nonexistent-key-id")
    assert response.status_code == 404


def test_delete_api_key_requires_auth(client):
    response = client.delete("/api/v1/keys/test-key-id")
    assert response.status_code == 401


def test_user_can_delete_own_api_key(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    key_resp = client.post(f"/api/v1/users/{user_id}/keys")
    key_id = key_resp.get_json()["apikey"]["apikey_id"]
    
    response = client.delete(f"/api/v1/keys/{key_id}")
    assert response.status_code == 200


def test_salesman_cannot_delete_other_user_api_key(client):
    name1 = _generate_name(10) + _generate_name(10)
    email1 = name1.lower() + "@example.com"
    password1 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name1,
        "email": email1,
        "password": password1,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id1 = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email1,
        "password": password1
    })
    assert response.status_code == 200
    key_resp = client.post(f"/api/v1/users/{user_id1}/keys")
    key_id = key_resp.get_json()["apikey"]["apikey_id"]
    
    name2 = _generate_name(10) + _generate_name(10)
    email2 = name2.lower() + "@example.com"
    password2 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name2,
        "email": email2,
        "password": password2,
        "role": "salesman"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email2,
        "password": password2
    })
    assert response.status_code == 200
    
    response = client.delete(f"/api/v1/keys/{key_id}")
    assert response.status_code == 403


def test_admin_can_delete_any_user_api_key(client):
    name1 = _generate_name(10) + _generate_name(10)
    email1 = name1.lower() + "@example.com"
    password1 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name1,
        "email": email1,
        "password": password1,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id1 = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email1,
        "password": password1
    })
    assert response.status_code == 200
    key_resp = client.post(f"/api/v1/users/{user_id1}/keys")
    key_id = key_resp.get_json()["apikey"]["apikey_id"]
    
    name2 = _generate_name(10) + _generate_name(10)
    email2 = name2.lower() + "@example.com"
    password2 = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name2,
        "email": email2,
        "password": password2,
        "role": "admin"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email2,
        "password": password2
    })
    assert response.status_code == 200
    
    response = client.delete(f"/api/v1/keys/{key_id}")
    assert response.status_code == 200


def test_delete_nonexistent_api_key(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "salesman"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    response = client.delete("/api/v1/keys/nonexistent-key-id")
    assert response.status_code == 404

def test_api_use(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "salesman"
    })
    assert response.status_code == 201
    user_id = response.get_json()["user_id"]
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200

    apikey = client.post(f"/api/v1/users/{user_id}/keys")
    assert apikey.status_code == 201
    apikey_id = apikey.get_json()["apikey"]["apikey_id"]
    headers = {
        "X-API-KEY": apikey_id
    }
    
    receipt = client.get("/api/v1/self", headers=headers)
    assert receipt.status_code == 200
    data = receipt.get_json()
    assert data["user"]["user_id"] == user_id
