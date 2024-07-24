import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from services.token_service import TokenService
from api.v1.routes.verify_magic_link import router
from database import get_db, Base
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


# Setup test app
app = FastAPI()
app.include_router(router)

# Create an in-memory SQLite database and bind the session
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Mock database dependency
@pytest.fixture
def mock_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mock TokenService dependency
@pytest.fixture
def mock_token_service():
    yield MockTokenService(valid_tokens=["valid_token"], invalid_tokens=["expired_token"])

# Create a mock app and override dependencies using dependency_overrides
@pytest.fixture
def test_app(mock_db, mock_token_service):
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[TokenService] = lambda: mock_token_service
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

def test_invalid_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "invalid_token"})
    assert response.status_code == 400

def test_expired_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "expired_token"})
    assert response.status_code == 400


def test_special_characters_token(test_app):
    client = TestClient(test_app)
    response = client.post("/api/v1/auth/verify-magic-link", json={"token": "!@#$%^&*()"})
    assert response.status_code in [200, 400]
