import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from api.db.database import get_db, get_db_engine, Base


load_dotenv()


db_url = os.getenv("DB_URL", "sqlite:///./test.db")
test_engine = create_engine(db_url, connect_args={
                            "check_same_thread": False} if "sqlite" in db_url else {})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine)


Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope="function")
def test_db():

    session = TestingSessionLocal()
    try:
        yield session
    finally:

        Base.metadata.drop_all(bind=test_engine)
        session.close()


@pytest.fixture(scope="function")
def client_with_mocks(test_db):
    # Patch the get_db dependency to use the test_db session
    with patch('api.db.database.get_db', lambda: test_db):
        with TestClient(app) as client:
            yield client


def test_signup_waitlist(client_with_mocks, mocker):
    mocker.patch('api.utils.rate_limiter.rate_limit', return_value=MagicMock())
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
    # Mock rate_limit decorator
    mocker.patch('api.utils.rate_limiter.rate_limit', return_value=MagicMock())
    for _ in range(5):
        client_with_mocks.post(
            "/api/v1/waitlist", json={"email": f"test{_}@example.com", "full_name": "Test User"})
    response = client_with_mocks.post(
        "/api/v1/waitlist", json={"email": "toomany@example.com", "full_name": "Test User"})
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]
