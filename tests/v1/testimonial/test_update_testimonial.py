import pytest
from main import app
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from api.db.database import get_db
import uuid

client = TestClient(app)

global_access_token = None

data = [
    {
        "client_name": "firsttestclientname",
        "author_id": "066a16d8-cab5-7dd3-8000-3a167556bb49",
        "content": "I love python",
        "id": "066a6e8b-f008-7242-8000-8f090997097c",
        "updated_at": "2025-01-01T01:56:31.002967+01:00",
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
            "password": "Testpassword",
            "first_name": "Test",
            "last_name": "User",
            "email": email,
        },
    )
    print("USER RESPONSE", user_response.json())

    if user_response.status_code != 201:
        raise Exception(f"Setup failed: {user_response.json()}")

    global global_access_token
    global_access_token = user_response.json()["data"]["access_token"]


def test_update_testimonial_success(db_session_mock):
    db_session_mock.query().filter().first.return_value = data[0]
    db_session_mock.commit.return_value = None

    update_data = {
        "content": "I love python (updated)",
    }

    response = client.put(
        f"/api/v1/testimonials/{data[0]['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {global_access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["messgae"] == "Your testimonial has been updated successfully."


def test_update_testimonial_not_found(db_session_mock):
    db_session_mock.query().filter().first.return_value = None

    update_data = {"content": "This is an updated testimonial."}

    response = client.put(
        "/api/v1/testimonials/non_existent_id",
        json=update_data,
        headers={"Authorization": f"Bearer {global_access_token}"},
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Testimonial not found."


def test_update_testimonial_unauthorized(db_session_mock):
    db_session_mock.query().filter().first.return_value = data[0]

    update_data = {"content": "This is an updated testimonial."}

    response = client.put(
        f"/api/v1/testimonials/{data[0]['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {global_access_token}"},
    )

    assert response.status_code == 403
    assert response.json()["message"] == "Forbidden. unauthorized user access"