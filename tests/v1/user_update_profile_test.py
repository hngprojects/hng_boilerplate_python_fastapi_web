# test_user_update_profile.py

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
PROFILE_UPDATE_ENDPOINT = "/api/v1/profile/current-user"

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
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

def create_mock_user_profile(mock_user_service, mock_db_session):
    '''Create a new user profile'''
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_profile = Profile(
        id=str(uuid7()),
        pronouns="he/him",
        job_title="developer",
        department="backend",
        social="facebook",
        bio="a foody",
        phone_number="17045060889999",
        avatar_url="avatalink",
        recovery_email="user@gmail.com",
        user_id=mock_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_profile
    return mock_profile

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_success_profile_update(mock_user_service, mock_db_session):
    """Test for successful profile update."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_profile = create_mock_user_profile(mock_user_service, mock_db_session)
    
    access_token = user_service.create_access_token(user_id=mock_user.id)  # Create a valid access token

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

    with patch.object(user_service, "get_current_user", return_value=mock_user):
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

    access_token = user_service.create_access_token(user_id=mock_user.id)  # Create a valid access token

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

    with patch.object(user_service, "get_current_user", return_value=mock_user):
        response = client.put(
            PROFILE_UPDATE_ENDPOINT,
            json=profile_update_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    response_data = response.json()
    assert response_data["detail"] == "Profile not found"
