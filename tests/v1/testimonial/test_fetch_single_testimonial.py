import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.models.testimonial import Testimonial
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from api.db.database import get_db
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
        del app.dependency_overrides[get_db]  # Ensure proper cleanup

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
        password="hashed_password",  # Use a mocked hash
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

def create_testimonial(mock_user_service, mock_db_session):
    """Create a mock testimonial in the mock database session."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
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
    return mock_testimonial

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_success_retrieval(mock_user_service, mock_db_session):
    """Test if the testimonial is fetched successfully."""
    
    with patch("api.v1.services.user.user_service.authenticate_user", return_value=True):
        with patch("api.v1.services.user.user_service.create_access_token", return_value="mocked_token"):
            create_mock_user(mock_user_service, mock_db_session)
            access_token = "mocked_token"
            
            # Ensure testimonial is already created
            testimonial = create_testimonial(mock_user_service, mock_db_session)
            
            # Retrieve testimonial
            response = client.get(
                f'/api/v1/testimonials/{testimonial.id}', 
                headers={'Authorization': f'Bearer {access_token}'}
            )

            print(response.json())
            assert response.status_code == status.HTTP_200_OK
            assert response.json().get("message") == f'Testimonial {testimonial.id} retrieved successfully'
            assert response.json().get("data").get("content") == testimonial.content

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_invalid_cred(mock_user_service, mock_db_session):
    """Test retrieval with invalid credentials"""
    
    response = client.get('/api/v1/testimonials/12345')  # Provide an actual ID
    print(response.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
