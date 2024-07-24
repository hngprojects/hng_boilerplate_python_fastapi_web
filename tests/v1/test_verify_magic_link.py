import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from api.v1.services.user import UserService
from api.v1.routes.verify_magic_link import router
from api.db.database import get_db

# Setup test app
app = FastAPI()
app.include_router(router, prefix="/api/v1")

# Mock UserService implementation
class MockUserService:
    def __init__(self, valid_tokens=None, invalid_tokens=None):
        self.valid_tokens = valid_tokens or []
        self.invalid_tokens = invalid_tokens or []

    def create_access_token(self, user_id: str) -> str:
        return f"auth_token_for_{user_id}"

    def verify_access_token(self, token: str, credentials_exception):
        if token in self.valid_tokens:
            return {"id": "user_id_for_valid_token"}
        elif token in self.invalid_tokens:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        else:
            raise credentials_exception

    def invalidate_token(self, db: Session, token: str):
        pass

# Mock database dependency
@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

# Mock UserService dependency
@pytest.fixture
def mock_user_service():
    return MockUserService(valid_tokens=["valid_token"], invalid_tokens=["expired_token", "invalid_token"])

# Setup the test client with overridden dependencies
@pytest.fixture
def client(db_session_mock, mock_user_service):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    app.dependency_overrides[UserService] = lambda: mock_user_service
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

# Test cases
def test_empty_token(client):
    response = client.post("/auth/verify-magic-link", json={"token": ""})
    assert response.status_code == 422

def test_whitespace_token(client):
    response = client.post("/auth/verify-magic-link", json={"token": " "})
    assert response.status_code == 422

def test_min_length_token(client):
    response = client.post("/auth/verify-magic-link", json={"token": "a"})
    assert response.status_code in [200, 400]

def test_valid_token(client):
    response = client.post("/auth/verify-magic-link", json={"token": "valid_token"})
    assert response.status_code == 200
    assert "auth_token" in response.json()
    assert response.json()["status"] == 200

def test_invalid_token(client):
    response = client.post("/auth/verify-magic-link", json={"token": "invalid_token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid or expired token"}

def test_expired_token(client):
    response = client.post("/auth/verify-magic-link", json={"token": "expired_token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid or expired token"}

def test_special_characters_token(client):
    response = client.post("/auth/verify-magic-link", json={"token": "!@#$%^&*()"})
    assert response.status_code in [200, 400]
