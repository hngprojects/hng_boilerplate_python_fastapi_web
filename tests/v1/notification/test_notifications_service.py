import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.models.user import User
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

def create_test_token(user_id: str) -> str:
    """Function to create a test token"""
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    data = {"user_id": user_id, "exp": expires}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def test_send_notification(db_session_mock):
    user = User(
        id="user_id",
        email="user@example.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch("api.utils.dependencies.get_current_user", return_value=user):
        token = create_test_token("user_id")

        response = client.post(
            "/api/v1/notifications/send",
            json={
                "user_id": "user1_id",
                "title": "Test Notification",
                "message": "This is a test notification."
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 201
    assert response.json()["message"] == "Notification sent successfully"
    assert response.json()["data"]["user_id"] == "user1_id"
    assert response.json()["data"]["title"] == "Test Notification"
    assert response.json()["data"]["message"] == "This is a test notification."
    assert response.json()["data"]["status"] == "unread"



