import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

from main import app
from api.v1.models import User
from api.v1.models.activity_log import ActivityLog
from api.v1.schemas.activity_log import ActivityLogResponse
from api.db.database import get_db
from api.utils.dependencies import get_current_active_superuser

client = TestClient(app)

# Mock the dependencies
def override_get_db():
    db = MagicMock(spec=Session)
    return db

def override_get_current_active_superuser():
    superuser = User(
        id="superuser",
        username="superuser",
        email="superuser@example.com",
        password="fakehashedpassword",
        is_active=True,
        is_super_admin=True
    )
    return superuser

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_active_superuser] = override_get_current_active_superuser

@pytest.fixture(scope="module")
def test_db():
    db = MagicMock(spec=Session)
    yield db

def test_get_activity_logs_superuser(test_db):
    # Mock the database response for user
    test_db.query(User).filter(User.id == "user1").first.return_value = User(
        id="user1",
        username="user1",
        email="user1@example.com",
        is_active=True
    )
    # Mock the database response for activity logs
    test_db.query(ActivityLog).filter(ActivityLog.user_id == "user1").all.return_value = [
        ActivityLog(log_id="1", activity_type="login", description="User logged in", timestamp="2024-01-01T12:00:00Z", user_id="user1"),
        ActivityLog(log_id="2", activity_type="logout", description="User logged out", timestamp="2024-01-01T14:00:00Z", user_id="user1")
    ]

    response = client.get(
        "/api/v1/activity-logs/user1",
        headers={"Authorization": "Bearer superuser"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Activity logs retrieved successfully"
    assert data["status_code"] == 200
    assert len(data["data"]) == 2
    assert data["data"][0]["log_id"] == "1"
    assert data["data"][1]["log_id"] == "2"
