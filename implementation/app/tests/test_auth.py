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


def test_register_user(client):
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
    data = response.get_json()
    assert data["result"] == "user registered"
    assert "user_id" in data

def test_register_user_and_login(client):
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
    data = response.get_json()
    assert data["result"] == "user registered"
    assert "user_id" in data

    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == "login success"


def test_register_user_and_login_and_check_user_id(client):
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
    data = response.get_json()
    assert data["result"] == "user registered"
    assert "user_id" in data
    user_id = data["user_id"]

    response = client.post("/api/v1/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == "login success"


    response = client.get("/api/v1/self")
    assert response.status_code == 200
    data = response.get_json()
    assert "user" in data
    user_info = data["user"]
    assert user_info["user_id"] == user_id
    assert user_info["name"] == name
    assert user_info["email"] == email
    assert user_info["role"] == role



def test_register_user_with_existing_email(client):
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
    data = response.get_json()
    assert data["result"] == "user registered"
    assert "user_id" in data

    response = client.post("/api/v1/register", json={
        "name": name,
        "email": email,
        "password": password,
        "role": role
    })
    assert response.status_code == 400

def test_login_with_wrong_password(client):
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
    data = response.get_json()
    assert data["result"] == "user registered"
    assert "user_id" in data

    wrong_password = "sejtpassword"
    response = client.post("/api/v1/login", json={
        "email": email,
        "password": wrong_password
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "invalid credentials"

def test_register_with_wrong_types(client):
    response = client.post("/api/v1/register", json={
        "name": 12345,
        "email": True,
        "password": [],
        "role": {"role": "salesman"}
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "wrong types provided"

def test_login_with_wrong_types(client):
    response = client.post("/api/v1/login", json={
        "email": 12345,
        "password": True
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "wrong types provided"


def test_register_with_insufficient_information(client):
    response = client.post("/api/v1/register", json={
        "name": "Test User",
        "email": ""})
    assert response.status_code == 400


def test_login_with_insufficient_information(client):
    response = client.post("/api/v1/login", json={
        "email": "cool@example.com"})
    assert response.status_code == 400

