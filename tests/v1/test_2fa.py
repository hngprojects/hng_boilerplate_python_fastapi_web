#!/usr/bin/python3
"""Test @FA endpoints"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...main import app
from api.utils.auth import hash_password, create_access_token
from api.db.database import get_db, Base
from api.v1.models.user import User
import pyotp

# Setup test database
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create tables in the test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(scope="module")
def test_user():
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="testuser@example.com",
        password=hash_password("testpassword"),
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()
    db.close()


@pytest.fixture(scope="module")
def test_token(test_user):
    return create_access_token(data={"username": test_user.username})


def test_enable_and_verify_2fa(test_user, test_token):
    # Enable 2FA
    response = client.post(
        "/api/v1/2fa/enable",
        json={"password": "testpassword"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "secret_key" in data

    # Verify 2FA
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == test_user.id).first()
    totp = pyotp.TOTP(user.secret_key)
    valid_code = totp.now()
    db.close()

    response = client.post(
        "/api/v1/2fa/verify",
        json={"totp_code": valid_code},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200


def test_login_with_2fa(test_user):
    # Enable 2FA for the user
    db = TestingSessionLocal()
    test_user.is_2fa_enabled = True
    test_user.secret_key = pyotp.random_base32()
    db.commit()
    db.refresh(test_user)
    totp = pyotp.TOTP(test_user.secret_key)
    valid_code = totp.now()
    db.close()

    # Attempt login with 2FA
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword"},
        params={"totp_code": valid_code}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_disable_2fa(test_user, test_token):
    db = TestingSessionLocal()
    test_user.is_2fa_enabled = True
    test_user.secret_key = pyotp.random_base32()
    db.commit()
    db.refresh(test_user)
    totp = pyotp.TOTP(test_user.secret_key)
    valid_code = totp.now()
    db.close()

    response = client.post(
        "/api/v1/2fa/disable",
        json={"current_password": "testpassword", "totp_code": valid_code},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200

    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == test_user.id).first()
    assert not user.is_2fa_enabled
    assert user.secret_key is None
    db.close()


if __name__ == "__main__":
    pytest.main([__file__])
