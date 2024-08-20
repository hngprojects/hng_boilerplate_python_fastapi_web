import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.models.testimonial import Testimonial
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from api.db.database import get_db
from api.utils.dependencies import get_super_admin
from fastapi import status
from datetime import datetime, timezone

LOGIN_ENDPOINT = 'api/v1/auth/login'
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
def mock_current_admin():
    """Fixture to mock the get_super_admin dependency."""

    with patch("api.utils.dependencies.get_super_admin", autospec=True) as mock_admin:
        mock_admin.return_value = User(
            id=str(uuid7()),
            email="testadmin@gmail.com",
            password=user_service.hash_password("Adminpassword@123"),
            first_name='Admin',
            last_name='User',
            is_active=True,
            is_superadmin=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        yield mock_admin

def create_mock_user(mock_user_service, mock_db_session, is_superadmin=True):
    """Create a mock user in the mock database session."""

    mock_user = User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=is_superadmin,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

def create_testimonial(mock_user_service, mock_db_session):
    """Create a mock testimonial in the mock database session."""

    mock_user = create_mock_user(mock_user_service, mock_db_session, is_superadmin=True)
    mock_testimonial = Testimonial(
        id=str(uuid7()),
        content='Product is good',
        author_id=mock_user.id,
        client_name="Client 1",
        client_designation="Client Designation",
        comments="Testimonial comments",
        ratings=4.5
    )
    mock_db_session.get.return_value = mock_testimonial
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_testimonial
    return mock_testimonial

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_delete_testimonial_unauthorized(mock_user_service, mock_db_session):
    """Test deletion without valid credentials."""

    app.dependency_overrides[user_service.get_current_user] = lambda: None
    response = client.delete(f'/api/v1/testimonials/234')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
