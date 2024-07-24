import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from api.v1.services.user import UserService
from api.v1.routes.verify_magic_link import verify_magic_link
from api.db.database import get_db
from ...main import app

# Mock UserService implementation
class MockUserService:
    def __init__(self, valid_tokens=None, invalid_tokens=None):
        self.valid_tokens = valid_tokens or []
        self.invalid_tokens = invalid_tokens or []

    def verify_access_token(self, token: str, credentials_exception):
        if token in self.valid_tokens:
            return {"id": "user_id_for_valid_token"}
        elif token in self.invalid_tokens:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        else:
            raise credentials_exception

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

@pytest.fixture(autouse=True)
def override_user_service():
    app.dependency_overrides[UserService] = lambda: MockUserService(valid_tokens=["valid_token"], invalid_tokens=["expired_token", "invalid_token"])

def test_valid_token(client):
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "valid_token"})
    assert response.status_code == 404
    assert "auth_token" in response.json()
    assert response.json()["status"] == 404

def test_invalid_token(client):
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "invalid_token"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid or expired token"}
