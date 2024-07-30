import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from ....main import app
from api.v1.routes.blog import get_db
from api.v1.models.notifications import Notification
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.utils.email_service import send_mail


# Mock database dependency
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


# Mock user service dependency

user_id = uuid7()
notification_id = uuid7()
timezone_offset = -8.0
tzinfo = timezone(timedelta(hours=timezone_offset))
timeinfo = datetime.now(tzinfo)
created_at = timeinfo
updated_at = timeinfo
access_token = user_service.create_access_token(str(user_id))

# Create test user

user = User(
    id=user_id,
    email="testuser1@gmail.com",
    password=user_service.hash_password("Testpassword@123"),
    first_name="Test",
    last_name="User",
    is_active=False,
    created_at=created_at,
    updated_at=updated_at,
)

# Create test notification

notification = Notification(
    id=notification_id,
    user_id=user_id,
    title="Test notification",
    message="This is my test notification message",
    status="unread",
    created_at=created_at,
    updated_at=updated_at,
)


def test_mark_notification_as_read(client, db_session_mock):

    db_session_mock.query().filter().all.return_value = [user, notification]

    headers = {"authorization": f"Bearer {access_token}"}

    response = client.patch(f"/api/v1/notifications/{notification.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["status_code"] == 200
    assert response.json()["message"] == "Notifcation marked as read"


def test_mark_notification_as_read_unauthenticated_user(client, db_session_mock):
    # Create test notification

    db_session_mock.query().filter().all.return_value = [notification]

    response = client.patch(f"/api/v1/notifications/{notification.id}")

    assert response.status_code == 401
    assert response.json()["success"] == False
    assert response.json()["status_code"] == 401
    
    
    
    

# New test cases for send_notification endpoint

def test_send_notification_success(client, monkeypatch):
    # Create a MagicMock object
    mock_send_mail = MagicMock(return_value=None)

    # Use monkeypatch to replace the send_mail function with the MagicMock
    monkeypatch.setattr("api.utils.email_service.send_mail", mock_send_mail)

    response = client.post(
        "/api/v1/notifications/send",
        json={
            "email": "recipient@example.com",
            "subject": "Test Notification",
            "message": "This is a test notification."
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "status_code": 200,
        "message": "Notification sent successfully",
        "data": {}
    }
    # Assert that the mock_send_mail was called once with the correct parameters
    mock_send_mail.assert_called_once_with(
        to="recipient@example.com",
        subject="Test Notification",
        body="This is a test notification."
    )

def test_send_notification_failure(client, monkeypatch):
    # Create a MagicMock object that raises an exception
    mock_send_mail = MagicMock(side_effect=Exception("SMTP error"))

    # Use monkeypatch to replace the send_mail function with the MagicMock
    monkeypatch.setattr("api.utils.email_service.send_mail", mock_send_mail)

    response = client.post(
        "/api/v1/notifications/send",
        json={
            "email": "recipient@example.com",
            "subject": "Test Notification",
            "message": "This is a test notification."
        }
    )

    assert response.status_code == 500
    assert "SMTP error" in response.json()["detail"]
    # Assert that the mock_send_mail was called once with the correct parameters
    mock_send_mail.assert_called_once_with(
        to="recipient@example.com",
        subject="Test Notification",
        body="This is a test notification."
    )