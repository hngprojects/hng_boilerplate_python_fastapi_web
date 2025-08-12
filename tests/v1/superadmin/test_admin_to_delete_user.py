import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from api.v1.models.user import User
from api.v1.schemas.user import AdminDeleteUserSchema
from api.db.database import get_db
from api.v1.services.user import user_service
from api.core.dependencies.google_email import mail_service
from datetime import datetime, timezone
from uuid_extensions import uuid7
from fastapi import status

client = TestClient(app)

@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}

@pytest.fixture
def super_admin_user():
    return User(
        id=str(uuid7()),
        email="superadmin@gmail.com",
        password=user_service.hash_password("Superpassword@123"),
        first_name="Super",
        last_name="Admin",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def regular_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def mock_get_current_user():
    """Fixture to create a mock current user"""
    with patch(
        "api.v1.services.user.UserService.get_current_user", autospec=True
    ) as mock_get_current_user:
        yield mock_get_current_user

from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."

    Yields:
        MagicMock: mock database
    """

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_mail_service():
    """Fixture to mock the mail service."""
    with patch("api.core.dependencies.google_email.mail_service.send_mail", autospec=True) as mock_service:
        yield mock_service

def test_deactivate_account_success(mock_db_session, mock_mail_service):
    """Test successful deactivation of a user account by a super admin"""
    mock_id = "mock_user_id"
    dummy_mock_user = User(
        id=mock_id,
        email="dummyuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Mr",
        last_name="Dummy",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    app.dependency_overrides[user_service.get_current_super_admin] = lambda: dummy_mock_user



    user = User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    

    response = client.post(
        "/api/v1/users/deactivate",
        json={"user_id": user.id, "token": "testtoken"},
        headers={"Authorization": "Bearer testtoken"},
    )
    response_json = response.json()
    
    
    mock_mail_service.assert_called_once()


    assert response.status_code == status.HTTP_200_OK
    assert response_json.get("status_code") == status.HTTP_200_OK
    assert response_json.get("message") == "User account deactivated successfully"


def test_deactivate_account_user_not_found(mock_db_session):
    """Test deactivation failure when the user ID does not exist"""
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: User(is_superadmin=True)

    mock_db_session.query().filter().first.return_value = None

    response = client.post(
        "/api/v1/users/deactivate",
        json={"user_id": "non_existent_user_id", "token": "testtoken"},
        headers={"Authorization": "Bearer testtoken"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["message"] == "User not found"
def test_deactivate_account_already_deactivated(mock_db_session):
    """Test that an already deactivated user cannot be deactivated again"""
    user = User(
        id="deactivated_user_id",
        email="inactiveuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Inactive",
        last_name="User",
        is_active=False,  
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    app.dependency_overrides[user_service.get_current_super_admin] = lambda: User(is_superadmin=True)
    
    
    mock_db_session.query().filter().first.return_value = user

    response = client.post(
        "/api/v1/users/deactivate",
        json={"user_id": "deactivated_user_id", "token": "testtoken"},
        headers={"Authorization": "Bearer testtoken"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["message"] == "User is already deactivated"


def test_deactivate_account_unauthorized(mock_db_session):
    """Test that a non-super-admin cannot deactivate a user account"""
    mock_id = "mock_user_id"
    non_admin_user = User(
        id=mock_id,
        email="regularuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Regular",
        last_name="User",
        is_active=True,
        is_superadmin=False,  
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: non_admin_user

    response = client.post(
        "/api/v1/users/deactivate",
        json={"user_id": "some_user_id", "token": "testtoken"},
        headers={"Authorization": "Bearer testtoken"},
    )

    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["message"] == "Only super admins can deactivate users"
