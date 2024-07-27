import os
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from main import app

client = TestClient(app)
LOGIN_ENDPOINT = "api/v1/auth/login"
CHANGE_PWD_ENDPOINT = "/api/v1/users/me/password"


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
        first_name="Test",
        last_name="User",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    return mock_user


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_autheniticated_user(mock_db_session, mock_user_service):

    mock_user = create_mock_user(mock_user_service, mock_db_session)

    login = client.post(
        LOGIN_ENDPOINT,
        data={"username": "testuser", "password": "Testpassword@123"},
    )
    access_token = login.json()["data"]["access_token"]

    user_pwd_change = client.patch(
        CHANGE_PWD_ENDPOINT,
        json={"old_password": "Testpassword@123", "new_password": "Ojobonandom@123"},
    )
    assert user_pwd_change.status_code == 401
    assert user_pwd_change.json()["message"] == "Not authenticated"


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_wrong_pwd(mock_db_session, mock_user_service):

    mock_user = create_mock_user(mock_user_service, mock_db_session)

    login = client.post(
        LOGIN_ENDPOINT,
        data={"username": "testuser", "password": "Testpassword@123"},
    )
    access_token = login.json()["data"]["access_token"]

    user_pwd_change = client.patch(
        CHANGE_PWD_ENDPOINT,
        json={"old_password": "Testpassw23", "new_password": "Ojobonandom@123"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_pwd_change.status_code == 400
    assert user_pwd_change.json()["message"] == "Incorrect old password"


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_user_password(mock_db_session, mock_user_service):

    mock_user = create_mock_user(mock_user_service, mock_db_session)

    login = client.post(
        LOGIN_ENDPOINT,
        data={"username": "testuser", "password": "Testpassword@123"},
    )
    access_token = login.json()["data"]["access_token"]

    user_pwd_change = client.patch(
        CHANGE_PWD_ENDPOINT,
        json={"old_password": "Testpassword@123", "new_password": "Ojobonandom@123"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_pwd_change.status_code == 200
    assert user_pwd_change.json()["message"] == "Password Changed successfully"
