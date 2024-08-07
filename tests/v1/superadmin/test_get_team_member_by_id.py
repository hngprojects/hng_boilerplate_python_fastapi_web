"""
Tests for superadmin
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.v1.models.team import TeamMember
from api.v1.services.team import TeamServices
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service, UserService
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone
from sqlalchemy.orm import Session


client = TestClient(app)
GET_TEAM_MEMBER_ENDPOINT = "/api/v1/team/members"


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."

    Yields:
        MagicMock: mock database
    """

    with patch("api.v1.services.user.get_db", autospec=True):
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""

    with patch("api.v1.services.user.user_service",
               autospec=True) as mock_service:
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
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None


def create_dummy_mock_team_member(mock_team_service: TeamServices, mock_db_session: Session):
    """generate a dummy mock team member in session

    Args:
        mock_user_service (UserService): mock user service
        mock_db_session (Session): mock database session
    """
    dummy_mock_user = TeamMember(
        id=mock_id,
        name="john doe",
        role="soft engineer",
        description="software engineer",
        picture_url="https://www.google.com",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db_session.get.return_value = dummy_mock_user
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_unauthorised_access(mock_user_service: UserService, mock_db_session: Session):
    """Test for unauthorized access to endpoint."""

    response = client.get(f"{GET_TEAM_MEMBER_ENDPOINT}/{str(uuid7())}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_non_admin_access(
    mock_get_current_user, mock_user_service: UserService, mock_db_session: Session
):
    """Test for non admin user access to endpoint"""

    mock_get_current_user.return_value = User(
        id=str(uuid7()),
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="AdminTest",
        last_name="User",
        is_active=False,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    response = client.get(
        f"{GET_TEAM_MEMBER_ENDPOINT}/{str(uuid7())}",
        headers={"Authorization": "Bearer dummy_token"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures(
    "mock_db_session", "mock_user_service", "override_get_current_super_admin"
)
def test_successful_team_member_get(
    mock_user_service: UserService,
    mock_db_session: Session,
    override_get_current_super_admin: None,
):
    """Test for successful get of team member"""

    # Create a mock user
    create_dummy_mock_user(mock_user_service, mock_db_session)
    mock_db_session.get.return_value = mock_db_session.get.return_value

    response = client.get(
        f"{GET_TEAM_MEMBER_ENDPOINT}/{mock_id}",
    )
    assert response.status_code == status.HTTP_200_OK

    # Simulate the user being deleted from the database
    mock_db_session.get.return_value = None

    response = client.get(
        f"{GET_TEAM_MEMBER_ENDPOINT}/{mock_id}",
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

    # Simulate the user not being found in the database
    mock_db_session.get.return_value = None

    response = client.get(
        f"{GET_TEAM_MEMBER_ENDPOINT}/{str(uuid7())}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
