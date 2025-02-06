import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.activity_logs import ActivityLog
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone, timedelta


client = TestClient(app)
ACTIVITY_LOGS_ENDPOINT = '/api/v1/activity-logs'


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""

    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service


def create_mock_user(mock_user_service, mock_db_session, is_superadmin=True):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=is_superadmin,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_activity_logs_empty(mock_user_service, mock_db_session):
    """Test for fetching all activity logs with no data."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    response = client.get(ACTIVITY_LOGS_ENDPOINT, headers={
                          'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_activity_logs_with_data(mock_user_service, mock_db_session):
    """Test for fetching all activity logs with data."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=str(uuid7()))

    log_id = str(uuid7())
    user_id = str(uuid7())
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)
    created_at = timeinfo
    updated_at = timeinfo

    activity_log = ActivityLog(
        id=log_id,
        user_id=user_id,
        action="profile Update",
        timestamp=timeinfo,
        created_at=created_at,
        updated_at=updated_at
    )

    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        activity_log]

    response = client.get(ACTIVITY_LOGS_ENDPOINT, headers={
                          'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_activity_logs_non_super_admin(mock_user_service, mock_db_session):
    """Test for fetching all activity logs as a non-super admin user."""
    mock_user = create_mock_user(
        mock_user_service, mock_db_session, is_superadmin=False)
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    response = client.get(ACTIVITY_LOGS_ENDPOINT, headers={
                          'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_403_FORBIDDEN
