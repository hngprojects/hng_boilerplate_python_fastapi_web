import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app  # Assuming your main app file is main.py
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.models.activity_logs import ActivityLog # Ensure you import your ActivityLog MODEL, not schema
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone, timedelta
from typing import List


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_activity_logs_default_pagination(mock_user_service, mock_db_session):
    """Test default pagination (no page/limit params)."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=str(uuid7()))

    # Mock 12 activity logs to test default limit of 10
    mock_logs = [
        create_mock_activity_log(str(uuid7()), str(uuid7()), f"action_{i}", datetime.now(timezone.utc))
        for i in range(12)
    ]
    mock_db_session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_logs[:10] # Mock first 10 for page 1

    response = client.get(ACTIVITY_LOGS_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 10  # Verify default limit is 10


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_activity_logs_limit_5(mock_user_service, mock_db_session):
    """Test setting limit to 5."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=str(uuid7()))

    mock_logs = [
        create_mock_activity_log(str(uuid7()), str(uuid7()), f"action_{i}", datetime.now(timezone.utc))
        for i in range(7) # Mock 7 logs, limit should return max 5
    ]
    mock_db_session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_logs[:5] # Mock first 5 for limit 5


    response = client.get(ACTIVITY_LOGS_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'}, params={'limit': 5})

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 5 # Verify limit is respected


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_activity_logs_page_2_limit_5(mock_user_service, mock_db_session):
    """Test getting page 2 with limit 5."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=str(uuid7()))

    mock_logs = [
        create_mock_activity_log(str(uuid7()), str(uuid7()), f"action_{i}", datetime.now(timezone.utc))
        for i in range(12) # Mock 12 logs
    ]
    mock_db_session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.side_effect = [ # Use side_effect to return different data for each page request
        mock_logs[:5], # Page 1 (items 0-4)
        mock_logs[5:10], # Page 2 (items 5-9)
        [] # Page 3 and beyond (empty list)
    ]

    response_page1 = client.get(ACTIVITY_LOGS_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'}, params={'page': 1, 'limit': 5})
    response_page2 = client.get(ACTIVITY_LOGS_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'}, params={'page': 2, 'limit': 5})
    response_page3 = client.get(ACTIVITY_LOGS_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'}, params={'page': 3, 'limit': 5})


    assert response_page1.status_code == status.HTTP_200_OK
    assert len(response_page1.json()) == 5
    assert response_page2.status_code == status.HTTP_200_OK
    assert len(response_page2.json()) == 5
    assert response_page3.status_code == status.HTTP_200_OK
    assert len(response_page3.json()) == 0 # Page 3 should be empty


# Add more pagination test cases here, like testing page beyond last page, etc.


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_activity_logs_empty(mock_user_service, mock_db_session):
    """Test for fetching all activity logs with no data."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    mock_db_session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [] # Mock empty list for no data
    response = client.get(ACTIVITY_LOGS_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [] # Verify empty list when no data


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_activity_logs_with_data(mock_user_service, mock_db_session):
    """Test for fetching all activity logs with data."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=str(uuid7()))

    mock_logs = [create_mock_activity_log(str(uuid7()), str(uuid7()), "profile Update", datetime.now(timezone.utc))]
    mock_db_session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_logs # Mock a single log

    response = client.get(ACTIVITY_LOGS_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 1 # Verify one log returned


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_activity_logs_non_super_admin(mock_user_service, mock_db_session):
    """Test for fetching all activity logs as a non-super admin user."""
    mock_user = create_mock_user(
        mock_user_service, mock_db_session, is_superadmin=False)
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    response = client.get(ACTIVITY_LOGS_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code 
