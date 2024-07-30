import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from ....main import app
from api.v1.routes.blog import get_db
from api.v1.models.notification_settings import NotificationSettings
from api.v1.services.user import user_service
from api.v1.models.user import User


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
user_id = str(uuid7())
timezone_offset = -8.0
tzinfo = timezone(timedelta(hours=timezone_offset))
timeinfo = datetime.now(tzinfo)
created_at = timeinfo
updated_at = timeinfo

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

# Create test notification settings
notification_settings = NotificationSettings(
    user_id=user_id,
    email_notifications=True,
    sms_notifications=True,
    push_notifications=False,
    created_at=created_at,
    updated_at=updated_at,
)


def test_patch_notification_settings(client, db_session_mock):
    db_session_mock.query().filter().first.return_value = user
    db_session_mock.query().filter().all.return_value = [notification_settings]

    response = client.patch(
        f"/api/v1/notification-settings/{user_id}",
        json={
            "email_notifications": False,
            "sms_notifications": True,
            "push_notifications": False
        },
    )
    
    assert response.status_code == 200
    assert response.json()["data"]["email_notifications"] == False
    assert response.json()["data"]["sms_notifications"] == True
    assert response.json()["data"]["push_notifications"] == False


def test_patch_notification_settings_user_not_found(client, db_session_mock):
    db_session_mock.query().filter().first.return_value = None

    response = client.patch(
        f"/api/v1/notification-settings/{user_id}",
        json={
            "email_notifications": False,
            "sms_notifications": True,
            "push_notifications": False
        },
    )

    assert response.status_code == 404
    assert (
        response.json()["message"]
        == "Notification settings not found for the specified user"
    )
