import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from requests.models import Response
from main import app
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.db.database import get_db
from uuid_extensions import uuid7
from datetime import datetime, timezone
from fastapi import status
from fastapi.encoders import jsonable_encoder

client = TestClient(app)

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

@pytest.fixture
def mock_google_oauth_service():
    """Fixture to create a mock Google OAuth service."""
    with patch("api.v1.services.google_oauth.GoogleOauthServices", autospec=True) as mock_service:
        yield mock_service

@pytest.mark.usefixtures("mock_db_session", "mock_user_service", "mock_google_oauth_service")
def test_google_login_existing_user(mock_user_service, mock_google_oauth_service, mock_db_session):
    """Test Google login for an existing user."""
    email = "existinguser@example.com"
    mock_id_token = "mocked_id_token"

    # Mock user data
    mock_user = User(
        id=str(uuid7()),
        email=email,
        first_name='Existing',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    # Mock user service responses
    mock_user_service.get_user_by_email.return_value = mock_user
    mock_user_service.create_access_token.return_value = "mock_access_token"
    mock_user_service.create_refresh_token.return_value = "mock_refresh_token"

    # Mock Google OAuth token info response
    with patch("requests.get") as mock_get:
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"email": email}
        mock_get.return_value = mock_response

        # Perform the API request
        response = client.post("api/v1/auth/google", json={"id_token": "mock_id_token"})
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json["data"]["user"]["email"] == email

@pytest.mark.usefixtures("mock_db_session", "mock_user_service", "mock_google_oauth_service")
def test_google_login_new_user(mock_user_service, mock_google_oauth_service, mock_db_session):
    """Test Google login for a new user."""
    email = "newuser@gmail.com"
    mock_id_token = "mocked_id_token"

    # Mock Google OAuth token info response
    with patch("requests.get") as mock_get:
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"email": email}
        mock_get.return_value = mock_response

        # Mock user retrieval returning None (new user)
        mock_user_service.get_user_by_email.return_value = None

        # Mock the GoogleOauthServices create method
        mock_user = User(
            id=str(uuid7()),
            email=email,
            first_name='New',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # Perform the API request
        response = client.post("api/v1/auth/google", json={"id_token": mock_id_token})

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json["data"]["user"]["email"] == email