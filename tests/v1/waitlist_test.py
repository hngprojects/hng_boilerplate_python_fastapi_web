from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db_engine, get_db, Base
from sqlalchemy.orm import Session
import pytest

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    engine = get_db_engine()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_signup_waitlist(test_db):
    response = client.post(
        "/api/v1/waitlist",
        json={"email": "test@example.com", "full_name": "Test User"}
    )
    assert response.status_code == 201
    assert response.json() == {"message": "You are all signed up!"}


def test_invalid_email(test_db):
    response = client.post(
        "/api/v1/waitlist",
        json={"email": "invalid-email", "full_name": "Test User"}
    )
    assert response.status_code == 422


def test_duplicate_email(test_db):
    client.post(
        "/api/v1/waitlist",
        json={"email": "duplicate@example.com", "full_name": "Test User"}
    )
    response = client.post(
        "/api/v1/waitlist",
        json={"email": "duplicate@example.com", "full_name": "Another User"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_rate_limiting(test_db):
    for _ in range(5):
        client.post(
            "/api/v1/waitlist",
            json={"email": f"test{_}@example.com", "full_name": "Test User"}
        )
    response = client.post(
        "/api/v1/waitlist",
        json={"email": "toomany@example.com", "full_name": "Test User"}
    )
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]
