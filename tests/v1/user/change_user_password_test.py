import os
from main import app
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.db.database import get_db
from uuid_extensions import uuid7
from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone


client = TestClient(app)
LOGIN_ENDPOINT = "api/v1/auth/login"
CHANGE_PWD_ENDPOINT = "/api/v1/auth/change-password"
p1 = os.getenv("TEST_PASSWORD_1", "Testmyname1!")  # This is a test password, safe to ignore.
p2 = os.getenv("TEST_PASSWORD_2", "Testmyname1!2")  # This is a test password, safe to ignore.
p3 = os.getenv("TEST_PASSWORD_2", "Testmyname1!23")  # This is a test password, safe to ignore.

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

    with patch("api.v1.services.user.user_service", autospec=True) as mock_service_class:
        mock_service_instance = mock_service_class.return_value
        yield mock_service_instance


def create_mock_user(mock_user_service, mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password(p1),
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
        json={"email": "testuser@gmail.com", "password": p1},
    )
    access_token = login.json()["access_token"]

    user_pwd_change = client.patch(
        CHANGE_PWD_ENDPOINT,
        json={"old_password": p1,
              "new_password": p2},
    )
    assert user_pwd_change.status_code == 401
    assert user_pwd_change.json()["message"] == "Not authenticated"


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_wrong_pwd(mock_db_session, mock_user_service):

    mock_user = create_mock_user(mock_user_service, mock_db_session)

    login = client.post(
        LOGIN_ENDPOINT,
        json={"email": "testuser@gmail.com", "password": p1},
    )
    access_token = login.json()["access_token"]

    user_pwd_change = client.patch(
        CHANGE_PWD_ENDPOINT,
        json={"old_password": p2,
              "new_password": p3},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_pwd_change.status_code == 400
    assert user_pwd_change.json()["message"] == "Incorrect old password"


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_user_password(mock_db_session, mock_user_service):

    mock_user = create_mock_user(mock_user_service, mock_db_session)

    login = client.post(
        LOGIN_ENDPOINT,
        json={"email": "testuser@gmail.com", "password": p1},
    )
    access_token = login.json()["access_token"]

    user_pwd_change = client.patch(
        CHANGE_PWD_ENDPOINT,
        json={"old_password": p1,
              "new_password": p2},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_pwd_change.status_code == 200
    assert user_pwd_change.json()["message"] == "Password changed successfully"
