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
        email="testuser@example.com",
        password=user_service.hash_password("TestPassword123!"),
        first_name="Test",
        last_name="User",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

def test_get_user_testimonials_success(mock_user_service, mock_db_session):
    """Test successful retrieval of user testimonials"""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    
    # Setup mock query for pagination
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []
    mock_query.count.return_value = 0
    
    mock_db_session.query.return_value = mock_query
    
    # Override dependency
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    response = client.get(
        f"/api/v1/testimonials/user/{mock_user.id}",
        headers={"Authorization": f"Bearer {user_service.create_access_token(str(mock_user.id))}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "items" in data["data"]
    assert "total" in data["data"]

def test_get_user_testimonials_unauthorized():
    """Test testimonial retrieval without authentication"""
    response = client.get(f"/api/v1/testimonials/user/some-id")
    assert response.status_code == 401
    data = response.json()
    assert data["message"] == "Not authenticated"

def test_get_user_testimonials_no_testimonials(mock_user_service, mock_db_session):
    """Test when user has no testimonials"""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    
    # Setup mock query for pagination
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []
    mock_query.count.return_value = 0
    
    mock_db_session.query.return_value = mock_query
    
    # Override dependency
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    response = client.get(
        f"/api/v1/testimonials/user/{mock_user.id}",
        headers={"Authorization": f"Bearer {user_service.create_access_token(str(mock_user.id))}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]["items"]) == 0
    assert data["data"]["total"] == 0
