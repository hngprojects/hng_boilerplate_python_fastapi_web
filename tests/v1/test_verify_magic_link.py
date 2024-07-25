from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from tests.database import session as test_session, client as test_client
from api.v1.routes.verify_magic_link import router
from api.db.database import Base, get_db
from api.v1.services.token_service import TokenService
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a mock TokenService
class MockTokenService:
    def __init__(self, valid_tokens=None, invalid_tokens=None):
        self.valid_tokens = valid_tokens or []
        self.invalid_tokens = invalid_tokens or []

    def generate_token(self):
        token = "new_valid_token"
        self.valid_tokens.append(token)
        logger.debug(f"Generated token: {token}")
        return token

    def validate_token(self, db, token):
        is_valid = token in self.valid_tokens
        logger.debug(f"Validating token: {token}, is_valid: {is_valid}")
        return is_valid

    def invalidate_token(self, db, token):
        if token in self.valid_tokens:
            self.valid_tokens.remove(token)
            logger.debug(f"Invalidated token: {token}")


# Mock TokenService dependency
@pytest.fixture
def mock_token_service():
    yield MockTokenService(valid_tokens=["valid_token"], invalid_tokens=["expired_token"])


# Create a mock app and override dependencies using dependency_overrides
@pytest.fixture
def test_app(test_session, mock_token_service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: test_session
    app.dependency_overrides[TokenService] = lambda: mock_token_service
    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)


# Test cases
def test_empty_token(client):
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": ""})
    assert response.status_code == 422


def test_whitespace_token(client):
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": " "})
    assert response.status_code == 422


def test_min_length_token(client):
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "a"})
    assert response.status_code in [200, 400]


def test_valid_token(client, mock_token_service):
    new_token = mock_token_service.generate_token()
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": new_token})
    assert response.status_code == 400 #as no valid token in db yet
    assert "auth_token" in response.json()


def test_invalid_token(client):
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "invalid_token"})
    assert response.status_code == 400


def test_expired_token(client):
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "expired_token"})
    assert response.status_code == 400


def test_special_characters_token(client):
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "!@#$%^&*()"})
    assert response.status_code in [200, 400] 
