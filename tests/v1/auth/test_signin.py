import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from api.v1.models.newsletter import Newsletter
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

# Mock the database dependency
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield
    # Clean up after the test by removing the override
    app.dependency_overrides = {}

def test_status_code(db_session_mock):
    # Arrange
    db_session_mock.query(Newsletter).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    user = {
        "username": "string",
        "password": "strin8Hsg263@",
        "first_name": "string",
        "last_name": "string",
        "email": "user@example.com"
    }

    # Act
    response = client.post("/api/v1/auth/register", json=user)

    print(response.json())

    # Assert
    assert response.status_code == 201

def test_user_login(db_session_mock):
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
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_user

    # Login with mock user details
    login = client.post("/api/v1/auth/login", data={
        "username": "testuser1",
        "password": "Testpassword@123"
    })
    response = login.json()
    assert response.get("status_code") == status.HTTP_200_OK