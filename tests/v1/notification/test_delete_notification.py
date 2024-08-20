import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from main import app
from api.v1.models.notifications import Notification
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.db.database import get_db


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

user_id = uuid7()
another_user_id = uuid7()
notification_id = 1
timezone_offset = -8.0
tzinfo = timezone(timedelta(hours=timezone_offset))
timeinfo = datetime.now(tzinfo)
created_at = timeinfo
updated_at = timeinfo
access_token = user_service.create_access_token(str(user_id))
another_user_access_token = user_service.create_access_token(str(another_user_id))

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

another_user = User(
    id=another_user_id,
    email="testuser2@gmail.com",
    password=user_service.hash_password("Testpassword@123"),
    first_name="Another",
    last_name="User",
    is_active=False,
    created_at=created_at,
    updated_at=updated_at,
)

# Create test notification
notification = Notification(
    user_id=user_id,
    title="Test notification",
    message="This is my test notification message",
    status="unread",
    created_at=created_at,
    updated_at=updated_at,
)

def test_delete_notification_unauthenticated_user(client, db_session_mock):
    db_session_mock.query().filter().first.return_value = notification

    response = client.delete(f"/api/v1/notifications/{notification.id}")

    assert response.status_code == 401

def test_delete_notification_unauthorized_user(client, db_session_mock):
    db_session_mock.query().filter().first.return_value = notification

    headers = {"authorization": f"Bearer {another_user_access_token}"}

    response = client.delete(f"/api/v1/notifications/{notification.id}", headers=headers)
    assert response.status_code == 403
    assert response.json()["message"] == "You do not have permission to delete this notification"
