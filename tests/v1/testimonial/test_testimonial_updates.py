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
        content='Original content',
        author_id=mock_user.id,
        client_name="Client 1",
        client_designation="Client Designation",
        comments="Testimonial comments",
        ratings=4.5
    )
    mock_db_session.get.return_value = mock_testimonial
    return mock_testimonial


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_update_testimonial_success(mock_user_service, mock_db_session):
    """Test successful update of a testimonial."""
    create_mock_user(mock_user_service, mock_db_session)

    login_response = client.post(LOGIN_ENDPOINT, json={
        "email": "testuser@gmail.com",
        "password": "Testpassword@123"
    })
    login_data = login_response.json()
    access_token = login_data.get('access_token')

    assert access_token, "Login failed, no access token returned"

    testimonial = create_testimonial(mock_user_service, mock_db_session)
    update_data = {"content": "Updated content"}

    # Send the update request
    update_response = client.put(
        f'/api/v1/testimonials/{testimonial.id}',
        json=update_data,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    update_response_data = update_response.json()
    print("Update Response:", update_response_data)  # Debugging log

    # Assert update request was successful
    assert update_response.status_code == status.HTTP_200_OK

    # Fetch the updated testimonial from the API
    fetch_response = client.get(
        f'/api/v1/testimonials/{testimonial.id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    fetch_data = fetch_response.json()
    print("Fetch Updated Testimonial:", fetch_data)  # Debugging log

    # Assert fetching the updated testimonial was successful
    assert fetch_response.status_code == status.HTTP_200_OK
    assert "data" in fetch_data, "Response missing 'data' key"
    assert "content" in fetch_data["data"], "Response missing 'content' key"
    assert fetch_data["data"]["content"] == "Updated content", \
        f"Expected content: 'Updated content', but got: {fetch_data['data']['content']}"


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_update_testimonial_not_found(mock_user_service, mock_db_session):
    """Test updating a non-existing testimonial."""
    create_mock_user(mock_user_service, mock_db_session)
    
    login_response = client.post(LOGIN_ENDPOINT, json={
        "email": "testuser@gmail.com",
        "password": "Testpassword@123"
    })
    login_data = login_response.json()
    access_token = login_data.get('access_token')

    assert access_token, "Login failed, no access token returned"

    non_existent_id = str(uuid7())
    update_data = {"content": "Updated content"}

    response = client.put(
        f'/api/v1/testimonials/{non_existent_id}',
        json=update_data,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    response_data = response.json()
    print("Not Found Response:", response_data)  # Debugging log

    expected_messages = [
        "Testimonial not found",
        "You do not have permission to update this testimonial",
        "Not authorized to update this testimonial"
    ]

    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]
    assert response_data.get("message") in expected_messages

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_update_testimonial_unauthorized():
    """Test updating a testimonial without authentication."""
    testimonial_id = str(uuid7())
    update_data = {"content": "Updated content"}

    response = client.put(f'/api/v1/testimonials/{testimonial_id}', json=update_data)
    response_data = response.json()
    
    print("Unauthorized Response:", response_data)  # Debugging log

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data.get("message") == "Not authenticated"
