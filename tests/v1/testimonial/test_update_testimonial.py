import pytest
from main import app
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from api.db.database import get_db
import uuid

client = TestClient(app)

data = [
    {
        "client_name": "firsttestclientname",
        "author_id": "066a16d8-cab5-7dd3-8000-3a167556bb49",
        "content": "I love python",
        "id": "066a6e8b-f008-7242-8000-8f090997097c",
        "updated_at": "2025-03-01T01:56:31.002967+01:00",
        "client_designation": "testclient",
        "comments": "I love testimonies",
        "ratings": 5.02,
        "created_at": "2025-01-01T01:56:31.002967+01:00",
    }
]


"""Mocking the database"""
@pytest.fixture
def mock_db():
    db_session = MagicMock()
    yield db_session


@pytest.fixture
def mock_id(mock_db):
    """Mock a database model."""
    mock_model = MagicMock()
    mock_model.query = MagicMock()
    mock_model.commit = MagicMock()
    mock_db.session = mock_model
    return mock_model


@pytest.fixture(autouse=True)
def override_get_db(mock_db):
    def get_db_override():
        yield mock_db

    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def setup_access_token():
    email = f"test{uuid.uuid4()}@gmail.com"

    user_response = client.post(
        "/api/v1/auth/register",
        json={
            "password": "@Testpassword2",
            "confirm_password": "@Testpassword2",
            "first_name": "Test",
            "last_name": "User",
            "email": email,
        },
    )

    assert user_response.status_code == 201, f"Setup failed {user_response.json()}"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "@Testpassword2"},
    )

    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"

    return login_response.json()["data"]["access_token"]


def test_update_testimonial_success(mock_id, setup_access_token):
    mock_id.query().filter().first.return_value = data[0]
    mock_id.commit = MagicMock()

    update_data = {
        "content": "I love python (updated)",
    }

    response = client.put(
        f"/api/v1/testimonials/{data[0]['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {setup_access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Your testimonial has been updated successfully."


def test_update_testimonial_not_found(mock_id, setup_access_token):
    mock_id.query().filter().first.return_value = None

    response = client.put(
        "/api/v1/testimonials/non_existent_id",
        json={"content": "This is an updated testimonial."},
        headers={"Authorization": f"Bearer {setup_access_token}"},
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Testimonial not found."


def test_update_testimonial_unauthorized(mock_id):
    response = client.put(
        f"/api/v1/testimonials/{data[0]['id']}",
        json={"content": "This is an updated testimonial."},
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Forbidden. unauthorized user access"
