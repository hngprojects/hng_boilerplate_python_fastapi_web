import sys
import os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from datetime import datetime, timezone
from fastapi import status
from api.db.database import get_db
from uuid_extensions import uuid7
from api.v1.services.user import user_service
from api.v1.models.user import User
from main import app
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)
DELETE_USER_ENDPOINT = '/api/v1/users/current-user/'


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


def create_mock_user(mock_user_service, mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=str(uuid7()),
        username="testuser",
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_successful_user_deletion(mock_user_service, mock_db_session):
    """Test for successful user deletion."""
    create_mock_user(mock_user_service, mock_db_session)

    login_response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    assert login_response.status_code == status.HTTP_200_OK
    access_token = login_response.json()['data']['access_token']

    delete_response = client.delete(DELETE_USER_ENDPOINT, headers={
                                   'Authorization': f'Bearer {access_token}'})
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_unauthorized_user_deletion(mock_user_service, mock_db_session):
    """Test for unauthorized user deletion."""
    delete_response = client.delete(DELETE_USER_ENDPOINT)
    assert delete_response.status_code == status.HTTP_401_UNAUTHORIZED