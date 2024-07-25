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
import jwt
import logging

# Import PyJWTError for error handling
from jwt import PyJWTError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = TestClient(app)
PROFILE_UPDATE_ENDPOINT = "/api/v1/profile/current-user"

SECRET_KEY = "your-secret-key"  # Ensure this matches your application settings
ALGORITHM = "HS256"

@pytest.fixture
def mock_db_session():
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_user_service():
    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        mock_instance = mock_service.return_value
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
            updated_at=datetime.now(timezone.utc)
        )
        mock_instance.get_current_user.return_value = mock_user
        mock_instance.create_access_token.return_value = jwt.encode({"user_id": mock_user.id}, SECRET_KEY, algorithm=ALGORITHM)
        yield mock_instance

def create_mock_profile(mock_db_session, user_id):
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
    logger.debug("Creating mock user")
    mock_user = mock_user_service.get_current_user()
    logger.debug(f"Mock user created: {mock_user}")

    logger.debug("Creating mock profile")
    create_mock_profile(mock_db_session, user_id=mock_user.id)

    logger.debug("Creating access token")
    access_token = mock_user_service.create_access_token(user_id=mock_user.id)
    logger.debug(f"Access token created: {access_token}")

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

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    logger.debug("Sending PUT request to update profile")
    response = client.put(
        PROFILE_UPDATE_ENDPOINT,
        json=profile_update_data,
        headers=headers,
    )

    logger.debug(f"Response received: {response.status_code} - {response.json()}")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["job_title"] == "Senior Software Engineer"

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_profile_update_not_found(mock_user_service, mock_db_session):
    logger.debug("Creating mock user")
    mock_user = mock_user_service.get_current_user()
    logger.debug(f"Mock user created: {mock_user}")

    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    logger.debug("Creating access token")
    access_token = mock_user_service.create_access_token(user_id=mock_user.id)
    logger.debug(f"Access token created: {access_token}")

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

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    logger.debug("Sending PUT request to update profile")
    response = client.put(
        PROFILE_UPDATE_ENDPOINT,
        json=profile_update_data,
        headers=headers,
    )

    logger.debug(f"Response received: {response.status_code} - {response.json()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Additional logging to verify the process

def test_token_generation(mock_user_service):
    mock_user = mock_user_service.get_current_user()
    access_token = mock_user_service.create_access_token(user_id=mock_user.id)
    logger.debug(f"Generated access token: {access_token}")
    expected_token = jwt.encode({"user_id": mock_user.id}, SECRET_KEY, algorithm=ALGORITHM)
    assert access_token == expected_token

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_current_user(mock_user_service, mock_db_session):
    mock_user = mock_user_service.get_current_user()
    logger.debug(f"Current mock user: {mock_user}")
    assert mock_user is not None
    assert mock_user.email == "testuser@gmail.com"
