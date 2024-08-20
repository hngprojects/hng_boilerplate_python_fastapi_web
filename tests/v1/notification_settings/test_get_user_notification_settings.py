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
        is_superadmin=False,
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


def test_fetch_user_notification_settings(client, db_session_mock):
    '''Test to successfully fetch a user's notification setting'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()
    app.dependency_overrides[notification_setting_service.fetch_by_user_id] = lambda: mock_settings()

    mock_notification_settings = mock_settings()

    with patch(
        "api.v1.services.notification_settings.notification_setting_service.fetch_by_user_id", 
        return_value=mock_notification_settings
    ) as mock_fetch:
        
        response = client.get(
            f'/api/v1/settings/notification-settings',
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 200


def test_unauthorized_user(client, db_session_mock):
    '''Test for unauthorized user'''

    mock_notification_settings = mock_settings()

    response = client.get(
        f'/api/v1/settings/notification-settings',
    )

    assert response.status_code == 401