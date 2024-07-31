from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.notifications import NotificationSetting
from api.v1.services.notification_settings import notification_setting_service
from main import app

def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="test@gmail.com",
        password=user_service.hash_password("Testuser@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_settings():
    return NotificationSetting(
        id=str(uuid7()),
        mobile_push_notifications=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


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

def test_create_user_notification_settings(client, db_session_mock):
    '''Test to successfully create new notification settings for the current user'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()
    app.dependency_overrides[notification_setting_service.create] = lambda db, user_id, schema: mock_settings()

    response = client.post(
        '/api/v1/settings/notification-settings',
        headers={'Authorization': 'Bearer token'},
        json={
            "mobile_push_notifications": True,
            "email_notification_activity_in_workspace": False,
            "email_notification_always_send_email_notifications": False,
            "email_notification_email_digest": False,
            "email_notification_announcement_and_update_emails": False,
            "slack_notifications_activity_on_your_workspace": True,
            "slack_notifications_always_send_email_notifications": False,
            "slack_notifications_announcement_and_update_emails": False
        }
    )

    assert response.status_code == 201
    assert response.json() == {
        "status_code": 201,
        "message": "Notification settings created successfully",
        "data": {
            "id": mock_settings().id,
            "mobile_push_notifications": True,
            "email_notification_activity_in_workspace": False,
            "email_notification_always_send_email_notifications": False,
            "email_notification_email_digest": False,
            "email_notification_announcement_and_update_emails": False,
            "slack_notifications_activity_on_your_workspace": True,
            "slack_notifications_always_send_email_notifications": False,
            "slack_notifications_announcement_and_update_emails": False
        }
    }

def test_create_notification_settings_missing_field(client, db_session_mock):
    '''Test to handle missing fields in notification settings creation'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()
    app.dependency_overrides[notification_setting_service.create] = lambda db, user_id, schema: mock_settings()

    response = client.post(
        '/api/v1/settings/notification-settings',
        headers={'Authorization': 'Bearer token'},
        json={
            "mobile_push_notifications": True
            # Missing other fields
        }
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', 'email_notification_activity_in_workspace']
    # Add more assertions based on validation errors

def test_create_notification_settings_unauthorized(client, db_session_mock):
    '''Test for unauthorized access to create notification settings'''

    response = client.post(
        '/api/v1/settings/notification-settings'
    )

    assert response.status_code == 401
