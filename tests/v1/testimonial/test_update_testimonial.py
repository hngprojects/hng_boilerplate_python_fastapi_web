import uuid
import pytest
from main import app
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from api.v1.models import Testimonial  # noqa: F403

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


@pytest.fixture(scope='module')
def mock_send_mail():
    """ For mocking the email send functionality """
    with patch("api.core.dependencies.email_sender.send_email") as mock_email_sending:
        with patch("fastapi.BackgroundTasks.add_task") as add_task_mock:
            add_task_mock.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)
            yield mock_email_sending


@pytest.fixture(scope="function")
def client_with_mocks(mock_send_mail):
    """For mocking a database connection and returning a test client"""
    with patch('api.db.database.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add.reset_mock()
        mock_db.commit.reset_mock()
        mock_db.refresh.reset_mock()

        yield client, mock_db

@pytest.fixture(autouse=True)
def setup_access_token(client_with_mocks):
    """For setting up an access token for authentication"""
    client, mock_db = client_with_mocks
    mock_db.query.return_value.filter.return_value.first.return_value = None

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
    assert user_response.status_code == 201, f"Setup failed: {user_response.json()}"
    return user_response.json()["data"]["access_token"]


def test_create_testimonial(client_with_mocks, setup_access_token):
    """Test to create testimonial"""
    client, mock_db = client_with_mocks

    payload = {
        "content": "I love python",
        "ratings": 5.02,
    }

    response = client.post(
        "api/v1/testimonials/",
        json=payload,
        headers={"Authorization": setup_access_token},
    )

    assert response.status_code == 201

    testimonial_id = response.json()["data"]["id"]
    testimonial = MagicMock()
    testimonial.content = payload["content"]
    testimonial.ratings = payload["ratings"]

    mock_db.query(Testimonial).get.return_value = testimonial
    retrieved_testimonial = mock_db.query(Testimonial).get(testimonial_id)

    assert retrieved_testimonial.content == payload["content"]
    assert retrieved_testimonial.ratings == payload["ratings"]

    return testimonial_id


def test_update_testimonial_success(client_with_mocks, setup_access_token):
    """Test to update testimonial successfully"""
    client, mock_db = client_with_mocks

    testimonial_id = test_create_testimonial(client_with_mocks, setup_access_token)

    mock_testimonial = MagicMock()
    mock_testimonial.id = uuid.UUID(testimonial_id)
    mock_testimonial.content = data[0]["content"]
    mock_testimonial.client_name = data[0]["client_name"]
    mock_testimonial.client_designation = data[0]["client_designation"]
    mock_testimonial.comments = data[0]["comments"]
    mock_testimonial.ratings = data[0]["ratings"]

    mock_db.query.return_value.filter.return_value.first.return_value = mock_testimonial

    update_data = {"content": "I love python (updated)"}

    response = client.put(
        f"/api/v1/testimonials/{data[0]['id']}",
        json=update_data,
        headers={"Authorization": setup_access_token},
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    assert response.json()["message"] == "Your testimonial has been updated successfully."


def test_update_testimonial_not_found(client_with_mocks, setup_access_token):
    """Test to update testimonial that does not exist"""
    client, mock_db = client_with_mocks

    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = client.put(
        "/api/v1/testimonials/non_existent_id",
        json={"content": "This is an updated testimonial."},
        headers={"Authorization": f"Bearer {setup_access_token}"},
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Testimonial does not exist"


def test_update_testimonial_unauthorized(client_with_mocks):
    """Test to update testimonial without authorization"""
    client, _ = client_with_mocks

    response = client.put(
        f"/api/v1/testimonials/{data[0]['id']}",
        json={"content": "This is an updated testimonial."},
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Could not validate credentials"
