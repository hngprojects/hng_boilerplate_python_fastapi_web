import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from main import app
from api.v1.models.token_login import TokenLogin
from api.v1.models.user import User
from api.v1.routes.auth import get_db

@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_request_signin_token(client, db_session_mock):
    # Mock user
    user = User(email="user@example.com")
    db_session_mock.query().filter().first.return_value = user

    response = client.post("/api/v1/auth/request-token", json={"email": "user@example.com"})

    assert response.status_code == 200
    assert response.json()["message"] == f"Sign-in token sent to {user.email}"
    

def test_verify_signin_token(client, db_session_mock):
    # Mock user with token
    user = TokenLogin(token="123456", expiry_time=datetime.utcnow() + timedelta(minutes=5))
    db_session_mock.query().filter().first.return_value = user

    response = client.post("/api/v1/auth/verify-token", json={"email": "user@example.com", "token": "123456"})

    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
