import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.models.profile import Profile
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone

client = TestClient(app)
PROFILE_UPDATE_ENDPOINT = "api/v1/profile/current-user"

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
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
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

def create_mock_profile(mock_db_session, user_id):
    """Create a mock profile in the mock database session."""
    mock_profile = Profile(
        id=str(uuid7()),
        user_id=user_id,
        pronouns="they/them",
        job_title="Software Engineer",
        department="Engineering",
        social='{"linkedin": "test"}',
        bio="Test bio",
        phone_number="+1234567890",
        avatar_url="http://example.com/avatar.png",
        recovery_email="test.recovery@example.com",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_profile
    return mock_profile

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_success_profile_update(mock_user_service, mock_db_session):
    """Test for successful profile update."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    create_mock_profile(mock_db_session, user_id=mock_user.id)

    access_token = user_service.create_access_token(user_id=mock_user.id)

    profile_update_data = {
        "pronouns": "they/them",
        "job_title": "Senior Software Engineer",
        "department": "Engineering",
        "social": '{"linkedin": "test_updated"}',
        "bio": "Updated test bio",
        "phone_number": "+1234567890",
        "avatar_url": "http://example.com/avatar_updated.png",
        "recovery_email": "test.recovery_updated@example.com",
    }

    response = client.put(
        PROFILE_UPDATE_ENDPOINT,
        json=profile_update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["job_title"] == "Senior Software Engineer"

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_profile_update_unauthorized(mock_user_service, mock_db_session):
    """Test for unauthorized profile update attempt."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)

    profile_update_data = {
        "pronouns": "they/them",
        "job_title": "Senior Software Engineer",
        "department": "Engineering",
        "social": '{"linkedin": "test_updated"}',
        "bio": "Updated test bio",
        "phone_number": "+1234567890",
        "avatar_url": "http://example.com/avatar_updated.png",
        "recovery_email": "test.recovery_updated@example.com",
    }

    response = client.put(
        PROFILE_UPDATE_ENDPOINT,
        json=profile_update_data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated"

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_profile_update_not_found(mock_user_service, mock_db_session):
    """Test for profile not found during update."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    access_token = user_service.create_access_token(user_id=mock_user.id)

    profile_update_data = {
        "pronouns": "they/them",
        "job_title": "Senior Software Engineer",
        "department": "Engineering",
        "social": '{"linkedin": "test_updated"}',
        "bio": "Updated test bio",
        "phone_number": "+1234567890",
        "avatar_url": "http://example.com/avatar_updated.png",
        "recovery_email": "test.recovery_updated@example.com",
    }

    response = client.put(
        PROFILE_UPDATE_ENDPOINT,
        json=profile_update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    response_data = response.json()
    assert response_data["detail"] == "Profile not found"
