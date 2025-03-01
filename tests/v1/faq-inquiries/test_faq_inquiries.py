from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.utils.send_mail import send_faq_inquiry_mail
from api.v1.models.faq_inquiries import FAQInquiries
from api.v1.models.user import User 
from api.v1.services.user import user_service
from main import app

# Create a mock superadmin user
mock_admin_user = User(id="1", is_superadmin=True)

@pytest.fixture
def db_session_mock():
    """Creates a mock database session."""
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    """Configures the test client with dependency overrides."""
    app.dependency_overrides[get_db] = lambda: db_session_mock
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_admin_user  # Returning User object, not a function
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def mock_post_inquiry():
    """Returns a mock FAQ inquiry object."""
    return FAQInquiries(
        id=str(uuid7()), 
        full_name="John Doe",
        email="john.doe@gmail.com",
        message="I have a question about the product.",
        user_id="1", 
    )

@patch('fastapi.BackgroundTasks.add_task')
@patch("api.v1.services.faq_inquiries.faq_inquiries_service.create")
def test_submit_faq_inquiries(mock_post_inquiry_form, mock_add_task, db_session_mock, client):
    """Tests the POST /api/v1/faq-inquiries endpoint to ensure successful submission with valid input."""
    mock_post_inquiry_form.return_value = mock_post_inquiry()

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    response = client.post('/api/v1/faq-inquiries', json={
        "full_name": "John Doe",
        "email": "johndoe@gmail.com",
        "message": "I have a question about the product."
    })

    assert response.status_code == 201

    mock_add_task.assert_called_once()
    mock_add_task.assert_called_with(
        send_faq_inquiry_mail,
        context={
            "full_name": "John Doe",
            "email": "john.doe@gmail.com",
            "message": "I have a question about the product.",
        }
    )

@patch("api.v1.services.faq_inquiries.faq_inquiries_service.fetch")
@patch("api.v1.services.faq_inquiries.faq_inquiries_service.delete")
def test_delete_faq_inquiry(mock_delete_inquiry, mock_fetch_inquiry, db_session_mock, client):
    """Tests the DELETE /api/v1/faq-inquiries/{id} endpoint to ensure successful deletion with valid authentication."""
    
    inquiry_id = str(uuid7())
    mock_fetch_inquiry.return_value = FAQInquiries(
        id=inquiry_id,
        full_name="John Doe",
        email="john.doe@gmail.com",
        message="I have a question about the product.",
        user_id="1",  # Matching with the mock_admin_user ID
    )

    db_session_mock.commit.return_value = None

    # Make a DELETE request with the mocked authentication
    response = client.delete(f'/api/v1/faq-inquiries/{inquiry_id}', headers={'Authorization': 'Bearer mock_token'})

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "status_code": 200,
        "message": "FAQ inquiry deleted successfully.",
        "data": {}
    }

    mock_fetch_inquiry.assert_called_once_with(db_session_mock, inquiry_id)
    mock_delete_inquiry.assert_called_once_with(db_session_mock, inquiry_id)
