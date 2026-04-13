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
def test_list_users_requires_auth(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


def test_list_users_when_authorized(client):
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
    
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "user_ids" in data
    assert isinstance(data["user_ids"], list)
    assert len(data["user_ids"]) >= 1


def test_list_users_contains_registered_user(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "admin"
    })
    assert response.status_code == 201
    user_id = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.get_json()
    assert user_id in data["user_ids"]


def test_get_user_info_requires_auth(client):
    response = client.get("/api/v1/users/some-user-id")
    assert response.status_code == 401


def test_get_user_info_nonexistent_user(client):
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
    
    response = client.get("/api/v1/users/nonexistent-user-id-12345")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_get_own_user_info(client):
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
    
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "user" in data
    user_info = data["user"]
    assert user_info["user_id"] == user_id
    assert user_info["email"] == email
    assert user_info["role"] == "salesman"


def test_salesman_cannot_view_other_user(client):
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
    
    response = client.get(f"/api/v1/users/{user_id2}")
    assert response.status_code == 403
    data = response.get_json()
    assert data["error"] == "forbidden"


def test_admin_can_view_any_user(client):
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
    
    response = client.get(f"/api/v1/users/{user_id1}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["user"]["user_id"] == user_id1


def test_get_self_endpoint(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "manager"
    })
    assert response.status_code == 201
    user_id = response.get_json()["user_id"]
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    response = client.get("/api/v1/self")
    assert response.status_code == 200
    data = response.get_json()
    assert "user" in data
    user_info = data["user"]
    assert user_info["user_id"] == user_id
    assert user_info["role"] == "manager"


def test_update_own_user_info(client):
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
    
    new_name = "Updated Name"
    new_password = _generate_password(12)
    response = client.post(f"/api/v1/users/{user_id}", json={
        "name": new_name,
        "password": new_password,
        "role": "salesman"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == "success"


def test_salesman_cannot_update_other_user(client):
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
    
    response = client.post(f"/api/v1/users/{user_id2}", json={
        "name": "Hacked Name",
        "password": _generate_password(12),
        "role": "admin"
    })
    assert response.status_code == 403


def test_admin_can_update_any_user(client):
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
    
    response = client.post(f"/api/v1/users/{user_id1}", json={
        "name": "New Name",
        "password": _generate_password(12),
        "role": "manager"
    })
    assert response.status_code == 200


def test_update_nonexistent_user(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "admin"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    response = client.post("/api/v1/users/nonexistent-id", json={
        "name": "Test",
        "password": _generate_password(12),
        "role": "salesman"
    })
    assert response.status_code == 404


def test_user_can_delete_self(client):
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
    
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200


def test_salesman_cannot_delete_other_user(client):
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
    
    response = client.delete(f"/api/v1/users/{user_id2}")
    assert response.status_code == 403


def test_admin_can_delete_any_user(client):
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
    
    response = client.delete(f"/api/v1/users/{user_id1}")
    assert response.status_code == 200


def test_delete_nonexistent_user(client):
    name = _generate_name(10) + _generate_name(10)
    email = name.lower() + "@example.com"
    password = _generate_password(12)
    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": "admin"
    })
    assert response.status_code == 201
    
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    
    response = client.delete("/api/v1/users/nonexistent-id")
    assert response.status_code == 404
