import pytest
from fastapi.testclient import TestClient
from jose import jwt
from ...main import app
from api.utils.dependencies import get_current_user, get_db
from api.db.database import get_db
from api.utils.config import SECRET_KEY, ALGORITHM


client = TestClient(app)

@pytest.fixture
def mock_get_current_user(monkeypatch):
    class FakeUser:
        id = 1

    def fake_get_current_user():
        return FakeUser()

    monkeypatch.setattr("api.utils.dependencies.get_current_user", fake_get_current_user)

@pytest.fixture
def mock_db_session(monkeypatch):
    class FakeSession:
        def query(self, *args, **kwargs):
            class Query:
                def filter(self, *args, **kwargs):
                    class Notification:
                        id = 1
                        user_id = 1
                        title = "Test Notification"
                        message = "This is a test notification."
                        status = "unread"

                    return [Notification()]

            return Query()

    monkeypatch.setattr("api.v1.routes.notificationroute.get_db", lambda: FakeSession())

def create_test_jwt_token():
    payload = {
        "sub": 1,
        "exp": 9999999999,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def test_get_user_notifications_success(mock_get_current_user, mock_db_session):
    valid_token = create_test_jwt_token()

    response = client.get(
        "/api/v1/notifications/current-user",
        headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Notifications fetched successfully",
        "status_code": 200,
        "data": {
            "notifications": [
                {
                    "id": 1,
                    "user_id": 1,
                    "title": "Test Notification",
                    "message": "This is a test notification.",
                    "status": "unread"
                }
            ]
        }
    }
