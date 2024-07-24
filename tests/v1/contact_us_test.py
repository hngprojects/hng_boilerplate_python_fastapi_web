from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models import User
from api.v1.services.user import user_service
from main import app
from fastapi import status

client = TestClient(app)
CONTACT_MESSAGES_ENDPOINT = "/api/v1/contact-us/messages"
LOGIN_ENDPOINT = '/api/v1/auth/login'


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


def create_mock_admin_user(mock_user_service, mock_db_session):
    """Create a mock admin user in the mock database session."""
    mock_admin_user = User(
        id=str(uuid7()),
        username="admintestuser",
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='AdminTest',
        last_name='User',
        is_active=True,
        is_super_admin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_admin_user
    return mock_admin_user


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_unauthorized_access(mock_user_service, mock_db_session):
    """Test for unauthorized access to endpoint."""
    response = client.get(CONTACT_MESSAGES_ENDPOINT)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_non_admin_access(mock_user_service, mock_db_session):
    """Test for non admin user access to endpoint"""
    mock_user = create_mock_user(mock_user_service, mock_db_session)

    login = client.post(LOGIN_ENDPOINT, data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    response = login.json()
    assert response.get("status_code") == status.HTTP_200_OK
    access_token = response.get('data').get('access_token')

    response = client.get(CONTACT_MESSAGES_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_fetch_contact_messages(mock_user_service, mock_db_session):
    """Test for successful fetching of contact messages"""
    mock_admin_user = create_mock_admin_user(mock_user_service, mock_db_session)

    login = client.post(LOGIN_ENDPOINT, data={
        "username": "admintestuser",
        "password": "Testpassword@123"
    })
    response = login.json()
    assert response.get("status_code") == status.HTTP_200_OK
    access_token = response.get('data').get('access_token')

    # Create a mock list of contact messages
    mock_contact_messages = [
        {
            "id": str(uuid7()),
            "full_name": "John Wick",
            "email": "test@wick.com",
            "title": "test title",
            "message": "Test message 1",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid7()),
            "full_name": "John Wick 2",
            "email": "test2@wick.com",
            "title": "test2 title",
            "message": "Test2 message 2",
            "created_at": datetime.now(timezone.utc)
        }
    ]

    mock_db_session.query.return_value.all.return_value = mock_contact_messages

    response = client.get(CONTACT_MESSAGES_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get("messages")) == len(mock_contact_messages)
