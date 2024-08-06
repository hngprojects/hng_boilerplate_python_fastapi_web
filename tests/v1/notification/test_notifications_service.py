import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.models.notifications import Notification
from api.db.database import get_db
from api.utils.settings import settings
import jwt

client = TestClient(app)

@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}

def create_test_token() -> str:
    """Function to create a test token"""
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    data = {"exp": expires}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def test_send_notification(db_session_mock):
    with patch("api.utils.dependencies.get_current_user", return_value=None):
        token = create_test_token()

        response = client.post(
            "/api/v1/notifications/send",
            json={
                "title": "Test Notification",
                "message": "This is a test notification."
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    print(response.json())  # Debug print
    assert response.status_code == 201
    assert response.json()["message"] == "Notification sent successfully"
    assert response.json()["data"]["title"] == "Test Notification"
    assert response.json()["data"]["message"] == "This is a test notification."
    assert response.json()["data"]["status"] == "unread"

def test_get_notification_by_id(db_session_mock):
    notification = Notification(
        id="notification_id",
        title="Notification",
        message="Message",
        status="unread",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db_session_mock.query().filter().first.return_value = notification

    with patch("api.utils.dependencies.get_current_user", return_value=None):
        token = create_test_token()

        response = client.get(
            f"/api/v1/notifications/{notification.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    print(response.json())  # Debug print
    assert response.status_code == 200
    assert response.json()["message"] == "Notification fetched successfully"
    assert response.json()["data"]["id"] == notification.id
    assert response.json()["data"]["title"] == notification.title
    assert response.json()["data"]["message"] == notification.message
    assert response.json()["data"]["status"] == notification.status

def test_get_all_notifications(db_session_mock):
    notification_1 = Notification(
        id="1",
        title="Notification 1",
        message="Message 1",
        status="unread",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    notification_2 = Notification(
        id="2",
        title="Notification 2",
        message="Message 2",
        status="unread",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db_session_mock.query().all.return_value = [notification_1, notification_2]

    with patch("api.utils.dependencies.get_current_user", return_value=None):
        token = create_test_token()

        response = client.get(
            "/api/v1/notifications/all",
            headers={"Authorization": f"Bearer {token}"},
        )

    print(response.json())  # Debug print
    assert response.status_code == 200
    assert response.json()["message"] == "Notification fetched successfully"
    
