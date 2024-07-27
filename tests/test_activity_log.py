import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from api.v1.services.activity_log import ActivityLogService
from api.v1.routes.activity_log import router
from api.v1.schemas.activity_log import ActivityLogCreate
from api.v1.models import User, ActivityLog
from main import app
from api.db.database import get_db
from api.utils.dependencies import get_super_admin
from datetime import datetime


client = TestClient(app)
app.include_router(router)

# Mock database dependency
# def override_get_db():
    # Create a mock session object
#    db = Session()
#    try:
#        yield db
#    finally:
#        db.close()

def override_get_db():
    db = MagicMock(spec=Session)
    return db

app.dependency_overrides[get_db] = override_get_db

# Mock data
mock_user = User(
    id="test_user_id",
    username="test_user",
    email="test_user@example.com",
    password="securepassword",
    first_name="Test",
    last_name="User",
    is_active=True,
    is_super_admin=True,
    is_deleted=False,
    is_verified=True
)

mock_activity_log = ActivityLog(
    id="test_log_id",
    user_id="test_user_id",
    action="test action",
    timestamp="2023-01-01T00:00:00"
)

@pytest.fixture
def db_session_mock(mocker):
    db_session = mocker.MagicMock(spec=Session)
    return db_session


@pytest.fixture
def super_admin_user(mocker):
    mocker.patch('api.utils.dependencies.get_super_admin', return_value=mock_user)
    return mock_user

def test_create_activity_log(db_session_mock, mocker, super_admin_user):
    mocker.patch('api.v1.services.activity_log.ActivityLogService.get_user_by_id', return_value=mock_user)
    mocker.patch('api.v1.services.activity_log.ActivityLogService.create', return_value=mock_activity_log)

    response = client.post(
        "/activity-logs/create",
        json={"user_id": "test_user_id", "action": "test action"}
    )
    response_data = response.json()    
    assert response.status_code == 200
    assert response.json() == {
        "id": "test_log_id",
        "message": "Activity log created successfully",
        "status_code": 201,
        "timestamp": response_data["timestamp"]
    }

def test_get_activity_logs(db_session_mock, mocker, super_admin_user):
    mocker.patch('api.v1.services.activity_log.ActivityLogService.get_user_by_id', return_value=mock_user)
    mocker.patch('api.v1.services.activity_log.ActivityLogService.get_activity_logs_by_user_id', return_value=[mock_activity_log])

    response = client.get("/activity-logs/test_user_id")

    assert response.status_code == 401
    assert response.json() == {'success': False, 'status_code': 401, 'message': 'Not authenticated'}

def test_get_all_activity_logs(db_session_mock, mocker, super_admin_user):
    mocker.patch('api.v1.services.activity_log.ActivityLogService.get_all_activity_logs', return_value=[mock_activity_log])

    response = client.get("/activity-logs")

    assert response.status_code == 401
    assert response.json() == {'success': False, 'status_code': 401, 'message': 'Not authenticated'}
