from datetime import timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password


def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data=data)

    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded


def test_create_access_token_custom_expiry():
    data = {"sub": "test@example.com"}
    expires_delta = timedelta(minutes=5)
    token = create_access_token(data=data, expires_delta=expires_delta)

    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded
