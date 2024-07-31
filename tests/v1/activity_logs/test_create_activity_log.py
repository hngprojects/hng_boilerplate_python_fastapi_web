import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.activity_logs import ActivityLog
from api.v1.services.activity_logs import activity_log_service
from api.db.database import get_db
from fastapi import status

client = TestClient(app)
CREATE_ACTIVITY_LOG_ENDPOINT = '/api/v1/activity-logs/create'

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_activity_log_service():
    """Fixture to create a mock activity log service."""
    with patch("api.v1.services.activity_logs.activity_log_service", autospec=True) as mock_service:
        yield mock_service

def create_mock_activity_log(mock_db_session, user_id: str, action: str):
    """Create a mock activity log in the mock database session."""
    mock_activity_log = ActivityLog(
        id=1,
        user_id=user_id,
        action=action,
        timestamp="2023-01-01T00:00:00"
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_activity_log
    return mock_activity_log

@pytest.mark.usefixtures("mock_db_session", "mock_activity_log_service")
def test_create_activity_log(mock_activity_log_service, mock_db_session):
    """Test for creating an activity log."""
    mock_user_id = "101"
    mock_action = "test_action"
    
    mock_activity_log = create_mock_activity_log(mock_db_session, mock_user_id, mock_action)
    mock_activity_log_service.create_activity_log.return_value = mock_activity_log
    
    response = client.post(
        CREATE_ACTIVITY_LOG_ENDPOINT,
        json={"user_id": mock_user_id, "action": mock_action}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "status_code": 201,
        "message": "Activity log created successfully",
        "success": True,
        "data": {
            "user_id": mock_activity_log.user_id,
            "action": mock_activity_log.action,
        }
    }
