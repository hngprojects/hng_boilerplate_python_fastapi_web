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
PROFILE_ENDPOINT = '/api/v1/profile/'
LOGIN_ENDPOINT = 'api/v1/auth/login'


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session. api.v1.services.user.get_db"""
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
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

def create_mock_user(mock_user_service, mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=str(uuid7()),
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
        username="testuser",
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
def test_errors(mock_user_service, mock_db_session):
    """Test for errors in profile creation"""
    create_mock_user(mock_user_service, mock_db_session)
    login = client.post(LOGIN_ENDPOINT, json={
        "email": "testuser@gmail.com",
        "password": "Testpassword@123"
    })
    response = login.json()
    assert response.get("status_code") == status.HTTP_200_OK
    access_token = response.get('data').get('user').get('access_token')

    missing_field = client.post(PROFILE_ENDPOINT, json={
        "username": "testuser",
        "job_title": "developer",
        "department": "backend",
        "social": "facebook",
        "bio": "a foody",
        "phone_number": "17045060889999",
        "avatar_url": "avatalink",
        "recovery_email": "user@gmail.com"
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert missing_field.status_code == 400 

    unauthorized_error = client.post(PROFILE_ENDPOINT, json={
        "username": "testuser",
        "pronouns": "male",
        "job_title": "developer",
        "department": "backend",
        "social": "facebook",
        "bio": "a foody",
        "phone_number": "17045060889999",
        "avatar_url": "avatalink",
        "recovery_email": "user@gmail.com"
    })
    assert unauthorized_error.status_code == 401


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_user_profile_exists(mock_user_service, mock_db_session):
    """Test for profile creation when profile already exists"""
    create_mock_user(mock_user_service, mock_db_session)
    login = client.post(LOGIN_ENDPOINT, json={
        "email": "testuser@gmail.com",
        "password": "Testpassword@123"
    })
    response = login.json()
    assert response.get("status_code") == status.HTTP_200_OK
    access_token = response.get('data').get('user').get('access_token')
    profile_exists = client.post(PROFILE_ENDPOINT, json={
        "username": "testuser",
        "pronouns": "he/him",
        "job_title": "developer",
        "department": "backend",
        "social": "facebook",
        "bio": "a foody",
        "phone_number": "17045060889999",
        "avatar_url": "avatalink",
        "recovery_email": "user@gmail.com"
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert profile_exists.status_code == 400
