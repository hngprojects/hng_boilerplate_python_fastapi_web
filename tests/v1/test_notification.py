import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from api.v1.models.notification import Notification as NotificationModel
from api.v1.models.user import User as UserModel
from api.v1.schemas.token import TokenData
from api.utils.dependencies import get_current_user
from api.v1.routes.notification import router as notifications_router

app = FastAPI()
app.include_router(notifications_router)

client = TestClient(app)

# Mock data for tests
mock_user = UserModel(id=1, username="testuser")
mock_notifications = [
    NotificationModel(id=1, user_id=1, message="Test Notification 1", read_status=False),
    NotificationModel(id=2, user_id=1, message="Test Notification 2", read_status=True),
]

@pytest.fixture
def mock_get_current_user(monkeypatch):
    async def _mock_get_current_user():
        return TokenData(username="testuser")
    monkeypatch.setattr("api.utils.dependencies.get_current_user", _mock_get_current_user)

@pytest.fixture
def mock_db_session(monkeypatch):
    class MockSession:
        def query(self, model):
            if model == UserModel:
                return MockQuery(mock_user)
            elif model == NotificationModel:
                return MockQuery(*mock_notifications)
            return MockQuery()

    class MockQuery:
        def __init__(self, *args):
            self.args = args

        def filter(self, *args):
            return self

        def all(self):
            return list(self.args)

        def first(self):
            return self.args[0] if self.args else None

    monkeypatch.setattr("api.v1.routes.notifications.get_db", lambda: MockSession())

def test_get_user_notifications_success(mock_get_current_user, mock_db_session):
    response = client.get(
        "/api/v1/notifications/current-user",
        headers={"Authorization": "Bearer valid_token"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Notifications fetched successfully",
        "status_code": 200,
        "data": {
            "notifications": [
                {"id": 1, "user_id": 1, "message": "Test Notification 1", "read_status": False},
                {"id": 2, "user_id": 1, "message": "Test Notification 2", "read_status": True}
            ]
        }
    }

# Dummy implementations for the sake of completeness
@app.get("/api/v1/notifications/current-user")
async def get_user_notifications(current_user: TokenData = Depends(get_current_user), db: Session = Depends(lambda: MockSession())):
    notifications = db.query(NotificationModel).filter(NotificationModel.user_id == current_user.id).all()
    return {
        "message": "Notifications fetched successfully",
        "status_code": 200,
        "data": {"notifications": [n.__dict__ for n in notifications]}
    }
