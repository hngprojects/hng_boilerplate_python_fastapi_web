# import sys, os
# import warnings

# warnings.filterwarnings("ignore", category=DeprecationWarning)
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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
DEACTIVATION_ENDPOINT = '/api/v1/users/deactivation'
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

    # mock_db_session.return_value.__enter__.return_value = mock_user
    # mock_user_service.hash_password.return_value = "hashed_password"
    # mock_db_session.add.return_value = None
    # mock_db_session.commit.return_value = None
    # mock_db_session.refresh.return_value = None

    return mock_user


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_error_user_deactivation(mock_user_service, mock_db_session):
    """Test for user deactivation errors."""

    mock_user = create_mock_user(mock_user_service, mock_db_session)
    
    # mock_user_service.get_current_user.return_value = create_mock_user(mock_user_service, mock_db_session)
    # login = client.post('/api/v1/auth/login', data={
    #     "username": "testuser",
    #     "password": "Testpassword@123"
    # })
    # result = login.json()
    # print(f"login: {result}")
    # assert result.get("success") == True
    # access_token = result['data']['access_token']
    access_token = user_service.create_access_token(user_id=str(uuid7()))

    # Missing field test
    missing_field = client.post(DEACTIVATION_ENDPOINT, json={
        "reason": "No longer need the account"
    }, headers={'Authorization': f'Bearer {access_token}'})
    
    assert missing_field.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Confirmation false test
    confirmation_false = client.post(DEACTIVATION_ENDPOINT, json={
        "reason": "No longer need the account",
        "confirmation": False
    }, headers={'Authorization': f'Bearer {access_token}'})
    
    assert confirmation_false.status_code == status.HTTP_400_BAD_REQUEST
    assert confirmation_false.json().get('message') == 'Confirmation required to deactivate account'

    # Unauthorized test
    unauthorized = client.post(DEACTIVATION_ENDPOINT, json={
        "reason": "No longer need the account",
        "confirmation": True
    })
    assert unauthorized.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_success_deactivation(mock_user_service, mock_db_session):
    """Test for successful user deactivation."""
    create_mock_user(mock_user_service, mock_db_session)

    login = client.post(LOGIN_ENDPOINT, data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    # mock_user_service.authenticate_user.return_value = create_mock_user(mock_user_service, mock_db_session)
    response = login.json()
    assert response.get("status_code") == status.HTTP_200_OK
    access_token = response.get('data').get('access_token')

    success_deactivation = client.post(DEACTIVATION_ENDPOINT, json={
        "reason": "No longer need the account",
        "confirmation": True
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert success_deactivation.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_user_inactive(mock_user_service, mock_db_session):
    """Test for inactive user deactivation."""

    # Create a mock user
    mock_user = User(
        id=str(uuid7()),
        username="testuser1",
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

    # Login with mock user details
    login = client.post(LOGIN_ENDPOINT, data={
        "username": "testuser1",
        "password": "Testpassword@123"
    })
    response = login.json()
    assert response.get("status_code") == status.HTTP_200_OK  # check for the right response before proceeding
    access_token = response.get('data').get('access_token')

    user_already_deactivated = client.post(DEACTIVATION_ENDPOINT, json={
        "reason": "No longer need the account",
        "confirmation": True
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert user_already_deactivated.status_code == 403
    assert user_already_deactivated.json().get('message') == 'User is not active'