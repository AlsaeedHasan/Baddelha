import pytest

from app.core.security import verify_password
from app.users.models import User
from tests.factories import UserFactory


def test_register_user(client, db_session):
    response = client.post(
        "/users/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

    # Verify in DB
    user = db_session.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert verify_password("password123", user.hashed_password)


def test_register_user_duplicate_email(client, db_session):
    UserFactory(email="existing@example.com")

    response = client.post(
        "/users/register",
        json={
            "email": "existing@example.com",
            "password": "password123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, db_session):
    user = UserFactory(email="login@example.com")
    # DEFAULT_PASSWORD is testpassword123! from factories

    response = client.post(
        "/users/login",
        json={
            "email": "login@example.com",
            "password": "testpassword123!",
            "full_name": "Login User",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_password(client, db_session):
    user = UserFactory(email="login@example.com")

    response = client.post(
        "/users/login",
        json={
            "email": "login@example.com",
            "password": "wrongpassword",
            "full_name": "Login User",
        },
    )
    assert response.status_code == 401


def test_get_profile(user_client):
    client, user = user_client
    response = client.get("/users/profile")

    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_update_profile(user_client, db_session):
    client, user = user_client
    response = client.put("/users/profile", json={"full_name": "Updated Name"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"

    db_session.refresh(user)
    assert user.full_name == "Updated Name"
