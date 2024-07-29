import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone


client = TestClient(app)
MAGIC_ENDPOINT = '/api/v1/auth/request-magic-link'


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""

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

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_request_magic_link(mock_user_service, mock_db_session):
    """Test for requesting magic link"""

    # Create a mock user
    mock_user = User(
        id=str(uuid7()),
        email="testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=False,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    with patch("api.utils.send_mail.smtplib.SMTP") as mock_smtp:
        # Configure the mock SMTP server
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance


        # Test for requesting magic link for an existing user
        magic_login = client.post(MAGIC_ENDPOINT, json={
            "email": mock_user.email
        })
        assert magic_login.status_code == status.HTTP_200_OK
        response = magic_login.json()
        #assert response.get("status_code") == status.HTTP_200_OK  # check for the right response before proceeding
        assert response.get("message") == f"Magic link sent to {mock_user.email}"

        # Ensure the SMTP server was called correctly
        #mock_smtp_instance.send_magic_link.assert_called_once()
        # Test for requesting magic link for a non-existing user
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        magic_login = client.post(MAGIC_ENDPOINT, json={
            "email": "notauser@gmail.com"
        })
        response = magic_login.json()
        assert response.get("status_code") == status.HTTP_404_NOT_FOUND  # check for the right response before proceeding
        assert response.get("message") == "User not found"