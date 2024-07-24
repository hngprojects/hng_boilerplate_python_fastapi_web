import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from ...main import app
from api.v1.models.testimonial import Testimonial
from api.db.database import get_db


@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    return db_session


@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_delete_all_testimonials(client):
    # Create multiple testimonials
    client.post(
        "/testimonials",
        json={"name": "Test User 1", "message": "Testimonial 1"}
    )
    client.post(
        "/testimonials",
        json={"name": "Test User 2", "message": "Testimonial 2"}
    )
    client.post(
        "/testimonials",
        json={"name": "Test User 3", "message": "Testimonial 3"}
    )

    # Delete all testimonials
    response = client.delete("/testimonials")
    assert response.status_code == 200
    assert response.json() == {
        "message": "All testimonials deleted successfully",
        "data": {},
        "status_code": 200
    }

    # Check that no testimonials are present
    response = client.get("/testimonials")
    assert response.status_code == 200
    assert response.json() == []
