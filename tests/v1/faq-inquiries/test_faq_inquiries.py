from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.utils.send_mail import send_faq_inquiry_mail
from api.v1.models.faq_inquiries import FAQInquiries
from main import app



@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def mock_post_inquiry():
    return FAQInquiries(
        id=str(uuid7()), 
        full_name="John Doe",
        email="john.doe@gmail.com",
        message="I have a question about the product.",
    )


@patch('fastapi.BackgroundTasks.add_task')
@patch("api.v1.services.faq_inquiries.faq_inquiries_service.create")
def test_submit_faq_inquiries(mock_post_inquiry_form, mock_add_task, db_session_mock, client):
    """Tests the POST /api/v1/newsletter-subscription endpoint to ensure successful subscription with valid input."""

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
