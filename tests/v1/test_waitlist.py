import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import uuid
from api.db.database import Base, get_db, SessionLocal, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():

    db_url = os.getenv("DB_URL", "sqlite:///./test.db")

    test_engine = create_engine(db_url)

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client_with_mocks(test_db):
    with patch('api.db.database.get_db', return_value=test_db):
        yield client


def test_signup_waitlist(client_with_mocks, mocker):

    mocker.patch('api.utils.rate_limiter.rate_limit', return_value=MagicMock())

    email = f"test{uuid.uuid4()}@example.com"

    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": email, "full_name": "Test User"}
    )

    assert response.status_code == 201
    assert response.json() == {"message": "You are all signed up!"}


def test_duplicate_email(client_with_mocks):
    client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "duplicate@example.com", "full_name": "Test User"}
    )
    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "duplicate@example.com", "full_name": "Another User"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_invalid_email(client_with_mocks):
    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "invalid_email", "full_name": "Test User"}
    )
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()[
        "detail"][0]["msg"]


def test_signup_with_empty_name(client_with_mocks):
    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "test@example.com", "full_name": ""}
    )
    assert response.status_code == 422
    assert "Full name is required" in response.json().get("detail", "")


def test_rate_limiting(client_with_mocks, mocker):

    mocker.patch('api.utils.rate_limiter.rate_limit', return_value=MagicMock())

    for _ in range(5):
        client_with_mocks.post(
            "/api/v1/waitlist",
            json={"email": f"test{_}@example.com", "full_name": "Test User"}
        )

    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "toomany@example.com", "full_name": "Test User"}
    )
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]
