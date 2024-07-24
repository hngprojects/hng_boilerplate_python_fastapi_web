import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from main import app

client = TestClient(app)


@pytest.fixture
def db_session_mock():
    """Create a mock database session."""
    db = MagicMock(spec=Session)
    yield db


def test_send_contact_message_success(db_session_mock):
    """Test sending a contact message successfully."""
    contact_message = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "title": "Test Message",
        "message": "This is a test message.",
    }
    response = client.post("/api/v1/contact-us", json=contact_message)

    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == contact_message["full_name"]
    assert data["email"] == contact_message["email"]
    assert data["title"] == contact_message["title"]
    assert data["message"] == contact_message["message"]


def test_send_contact_message_invalid_data(db_session_mock):
    """Test sending a contact message with invalid data."""
    invalid_contact_message = {
        "full_name": "",
        "email": "invalid-email",
        "title": "T",
        "message": "",
    }
    response = client.post("/api/v1/contact-us", json=invalid_contact_message)

    assert response.status_code == 422


def test_internal_server_error(db_session_mock):
    """Simulates an internal server error."""
    with patch(
        "api.v1.services.contact_us.ContactUsService.create_contact_message"
    ) as mock_method:
        mock_method.side_effect = Exception("Internal Server Error")

        contact_message = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "title": "Test Message",
            "message": "This is a test message.",
        }

        response = client.post("/api/v1/contact-us", json=contact_message)

        assert response.status_code == 500
        assert response.json() == {
            "message": "Internal server error.",
            "status_code": 500,
            "success": False,
        }


def test_invalid_method(db_session_mock):
    """Test handling of invalid HTTP method."""
    response = client.get("/api/v1/contact-us")

    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}
