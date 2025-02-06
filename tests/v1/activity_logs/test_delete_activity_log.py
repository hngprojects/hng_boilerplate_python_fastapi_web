import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from main import app
from api.v1.services.activity_logs import activity_log_service
from api.v1.models.activity_logs import ActivityLog
from api.v1.services.user import user_service

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    """Fixture to provide a mock database session."""
    mock_db = MagicMock()
    return mock_db

@pytest.fixture
def mock_user_service():
    """Fixture to mock the user service."""
    mock_user_service = MagicMock()
    mock_user_service.create_access_token.return_value = "mocked_access_token"
    mock_user_service.get_current_super_admin = MagicMock(return_value=MagicMock(is_superadmin=True))
    return mock_user_service

def test_delete_activity_log(mock_db_session, mock_user_service):
    """Test the delete activity log endpoint."""

    app.dependency_overrides[user_service.get_current_super_admin] = mock_user_service.get_current_super_admin
    activity_log_service.delete_activity_log_by_id = MagicMock(return_value={
        "status": "success",
        "detail": "Activity log with ID 1 deleted successfully"
    })

    access_token = mock_user_service.create_access_token(user_id="mocked_user_id")
    mock_db_session.query(ActivityLog).filter.return_value.first.return_value = ActivityLog(
        id=1,
        user_id="user_id",
        action="test_action"
    )

    response = client.delete(
        "/api/v1/activity-logs/1",
        headers={'Authorization': f'Bearer {access_token}'},
        params={'args': 'value', 'kwargs': 'value'}
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "Activity log with ID 1 deleted successfully"