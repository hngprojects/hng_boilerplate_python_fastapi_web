"""
Tests for superadmin
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service, UserService
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status, HTTPException
from datetime import datetime, timezone
from sqlalchemy.orm import Session


client = TestClient(app)
USER_DELETE_ENDPOINT = "/api/v1/superadmin/users"


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."

    Yields:
        MagicMock: mock database
    """

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        # mock_get_db.return_value.__enter__.return_value = mock_db
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""

    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service


@pytest.fixture
def mock_get_current_user():
    """Fixture to create a mock current user"""
    with patch(
        "api.v1.services.user.UserService.get_current_user", autospec=True
    ) as mock_get_current_user:
        yield mock_get_current_user


@pytest.fixture
def override_get_current_super_admin():
    """Mock the get_current_super_admin dependency"""

    app.dependency_overrides[user_service.get_current_super_admin] = lambda: User(
        id=str(uuid7()),
        username="admintestuser",
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="AdminTest",
        last_name="User",
        is_active=False,
        is_super_admin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


mock_id = str(uuid7())


def create_dummy_mock_user(mock_user_service: UserService, mock_db_session: Session):
    """generate a dummy mock user

    Args:
        mock_user_service (UserService): mock user service
        mock_db_session (Session): mock database session
    """
    dummy_mock_user = User(
        id=mock_id,
        username="dummyuser",
        email="dummyuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Mr",
        last_name="Dummy",
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db_session.get.return_value = dummy_mock_user


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_unauthorised_access(mock_user_service: UserService, mock_db_session: Session):
    """Test for unauthorized access to endpoint."""

    response = client.delete(f"{USER_DELETE_ENDPOINT}/{str(uuid7())}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_non_admin_access(
    mock_get_current_user, mock_user_service: UserService, mock_db_session: Session
):
    """Test for non admin user access to endpoint"""

    mock_get_current_user.return_value = User(
        id=str(uuid7()),
        username="admintestuser",
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="AdminTest",
        last_name="User",
        is_active=False,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    response = client.delete(
        f"{USER_DELETE_ENDPOINT}/{str(uuid7())}",
        headers={"Authorization": "Bearer dummy_token"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures(
    "mock_db_session", "mock_user_service", "override_get_current_super_admin"
)
def test_successful_deletion(
    mock_user_service: UserService,
    mock_db_session: Session,
    override_get_current_super_admin: None,
):
    """Test for successful deletion of user"""

    # Create a mock user
    create_dummy_mock_user(mock_user_service, mock_db_session)
    response = client.delete(
        f"{USER_DELETE_ENDPOINT}/{mock_id}",
    )
    assert response.status_code == status.HTTP_200_OK
    response = client.delete(
        f"{USER_DELETE_ENDPOINT}/{mock_id}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures(
    "mock_db_session", "mock_user_service", "override_get_current_super_admin"
)
def test_not_found_error(
    mock_user_service: UserService,
    mock_db_session: Session,
    override_get_current_super_admin: None,
):
    """Test for invalid user ID"""

    response = client.delete(
        f"{USER_DELETE_ENDPOINT}/{str(uuid7())}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
