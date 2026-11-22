from fastapi.testclient import TestClient
from api_trad import app

client = TestClient(app)


def test_login_success():
    response = client.post(
        "/token", data={"username": "johndoe", "password": "secret"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_incorrect_password():
    response = client.post(
        "/token", data={"username": "johndoe", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_nonexistent_user():
    response = client.post(
        "/token", data={"username": "janedoe", "password": "secret"}
    )
    assert response.status_code == 400


def test_create_user_unauthorized():
    # Trying to hit protected endpoint without providing a bearer token
    response = client.post(
        "/users/", json={"username": "newuser", "email": "new@example.com"}
    )
    assert response.status_code == 401


def test_create_user_authorized():
    # 1. First get a valid token
    login_res = client.post(
        "/token", data={"username": "johndoe", "password": "secret"}
    )
    token = login_res.json()["access_token"]

    # 2. Use the token to create a user via authorized header
    response = client.post(
        "/users/",
        json={"username": "newuser", "email": "new@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"username": "newuser", "email": "new@example.com"}


def test_create_user_invalid_payload():
    # Get a token first
    login_res = client.post(
        "/token", data={"username": "johndoe", "password": "secret"}
    )
    token = login_res.json()["access_token"]

    # Send missing required fields (e.g., missing email)
    response = client.post(
        "/users/",
        json={"username": "incompleteuser"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422