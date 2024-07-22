import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from decouple import config
from api.v1.models.user import WaitlistUser  
from api.v1.models.base import Base  
from api.db.database import get_db

# Load environment variables
load_dotenv()

# Database setup for testing
SQLALCHEMY_DATABASE_URL = config('DB_URL')
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

print(f"Tables created: {Base.metadata.tables.keys()}")


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="function")
def client_with_mocks(mocker, test_db):
    with patch('api.db.database.get_db', return_value=test_db):
        with patch('api.utils.rate_limiter.rate_limit', return_value=MagicMock()):
            yield client


def test_waitlist_signup(client_with_mocks, mocker):
    email = f"test{uuid.uuid4()}@example.com"
    response = client_with_mocks.post(
        "/api/v1/waitlist", json={"email": email, "full_name": "Test User"})
    assert response.status_code == 201
    assert response.json() == {"message": "You are all signed up!"}


def test_duplicate_email(client_with_mocks):
    client_with_mocks.post(
        "/api/v1/waitlist", json={"email": "duplicate@example.com", "full_name": "Test User"})
    response = client_with_mocks.post(
        "/api/v1/waitlist", json={"email": "duplicate@example.com", "full_name": "Another User"})
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_invalid_email(client_with_mocks):
    response = client_with_mocks.post(
        "/api/v1/waitlist", json={"email": "invalid_email", "full_name": "Test User"})
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()[
        "detail"][0]["msg"]


def test_signup_with_empty_name(client_with_mocks):
    response = client_with_mocks.post(
        "/api/v1/waitlist", json={"email": "test@example.com", "full_name": ""})
    assert response.status_code == 422
    assert "Full name is required" in response.json().get("detail", "")


def test_rate_limiting(client_with_mocks, mocker):
    for _ in range(5):
        client_with_mocks.post(
            "/api/v1/waitlist", json={"email": f"test{_}@example.com", "full_name": "Test User"})
    response = client_with_mocks.post(
        "/api/v1/waitlist", json={"email": "toomany@example.com", "full_name": "Test User"})
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]
