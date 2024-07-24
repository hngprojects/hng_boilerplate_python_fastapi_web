import pytest
from fastapi import FastAPI, HTTPException, Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.v1.services.user import UserService
from api.v1.routes.verify_magic_link import router
from api.db.database import get_db
from unittest.mock import MagicMock, patch
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Mock UserService implementation
class MockUserService:
    def __init__(self, valid_tokens=None, invalid_tokens=None):
        self.valid_tokens = valid_tokens or []
        self.invalid_tokens = invalid_tokens or []

    def create_access_token(self, user_id: str) -> str:
        return f"auth_token_for_{user_id}"

    def verify_access_token(self, token: str, credentials_exception):
        if token in self.valid_tokens:
            return user.TokenData(id="user_id_for_valid_token")
        elif token in self.invalid_tokens:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        else:
            raise credentials_exception

    def invalidate_token(self, db: Session, token: str):
        pass

# Setup test app
app = FastAPI()
app.include_router(router)

# Mock database dependency
@pytest.fixture
def mock_db():
    with patch('api.db.database.SessionLocal', autospec=True) as mock_session:
        yield mock_session()

# Mock UserService dependency
@pytest.fixture
def mock_user_service():
    return MockUserService(valid_tokens=["valid_token"], invalid_tokens=["expired_token", "invalid_token"])

# Create a mock app and override dependencies using dependency_overrides
@pytest.fixture
def test_app(mock_db, mock_user_service):
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[UserService] = lambda: mock_user_service
    yield app
    app.dependency_overrides.clear()

client = TestClient(app)

# Test cases
def test_empty_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": ""})
    assert response.status_code == 422

def test_whitespace_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": " "})
    assert response.status_code == 422

def test_min_length_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "a"})
    assert response.status_code in [200, 400]

def test_valid_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "valid_token"})
    assert response.status_code == 200
    assert "auth_token" in response.json()
    assert response.json()["status"] == 200

def test_invalid_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "invalid_token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid or expired token"}

def test_expired_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "expired_token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid or expired token"}

def test_special_characters_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "!@#$%^&*()"})
    assert response.status_code in [200, 400]
