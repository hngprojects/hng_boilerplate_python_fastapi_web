import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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

    return mock_user

def create_testimonial(mock_user_service, mock_db_session):
    """Create a mock testimonail in the mock database session."""
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
    """Test if the testimonial is fetched."""

    # get auth credentials
    create_mock_user(mock_user_service, mock_db_session)
    login = client.post(LOGIN_ENDPOINT, data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    response = login.json()
    access_token = response.get('data').get('access_token')

    # ensure testimonial is already created
    testimonial = create_testimonial(mock_user_service, mock_db_session)

    # retrieve testimonial
    response = client.get(f'/api/v1/testimonials/{testimonial.id}', headers={'Authorization': f'Bearer {access_token}'})
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == 'Testimonial {} retrieved successfully'.format(testimonial.id)
    assert response.json().get("data").get("content") == testimonial.content


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_invalid_testimonial(mock_user_service, mock_db_session):
    """Test for invalid testimonial id"""
    create_mock_user(mock_user_service, mock_db_session)
    login = client.post(LOGIN_ENDPOINT, data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    response = login.json()
    access_token = response.get('data').get('access_token')

    testimonial = create_testimonial(mock_user_service, mock_db_session)

    # retrieve invalid testimonial
    response = client.get(f'/api/v1/testimonials/234', headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("message") == 'Testimonial 234 not found'
    

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_invalid_cred(mock_user_service, mock_db_session):
    """Test with invalid credentials"""
    response = client.get(f'/api/v1/testimonials/234')
    print(response.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED