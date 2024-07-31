from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organization import Organization
from api.v1.services.user import UserService
from api.v1.services.organization import organization_service
from main import app

client = TestClient(app)

# Create a mock database session
@pytest.fixture
def db_session_mock():
    db = MagicMock()
    yield db
    db.close()

# Override the get_db dependency
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def _get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

# Mock the current user function
@pytest.fixture
def mock_get_current_user():
    with patch.object(UserService, 'get_current_user', return_value={"id": 1, "email": "test@example.com"}):
        yield

def test_get_organization_success(db_session_mock, mock_get_current_user):
    mock_organization = MagicMock(spec=Organization)
    mock_organization.id = "066aa666-d660-7c6c-8000-539423b940e3"
    mock_organization.created_at = datetime.now()
    mock_organization.updated_at = datetime.now()
    mock_organization.company_name = "Updated Organization"
    mock_organization.company_email = "updated@gmail.com"
    mock_organization.industry = "Tech"
    mock_organization.organization_type = "Tech"
    mock_organization.country = "Nigeria"
    mock_organization.state = "Lagos"
    mock_organization.address = "Ikorodu, Lagos"
    mock_organization.lga = "Ikorodu"

    db_session_mock.query().filter().first.return_value = mock_organization

    response = client.get("/api/v1/organizations/1", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["status_code"] == 200
    assert data["data"]["id"] == "066aa666-d660-7c6c-8000-539423b940e3"
    assert data["data"]["created_at"] == mock_organization.created_at.isoformat()
    assert data["data"]["updated_at"] == mock_organization.updated_at.isoformat()
    assert data["data"]["company_name"] == "Updated Organization"
    assert data["data"]["company_email"] == "updated@gmail.com"
    assert data["data"]["industry"] == "Tech"
    assert data["data"]["organization_type"] == "Tech"
    assert data["data"]["country"] == "Nigeria"
    assert data["data"]["state"] == "Lagos"
    assert data["data"]["address"] == "Ikorodu, Lagos"
    assert data["data"]["lga"] == "Ikorodu"

def test_get_organization_not_found(db_session_mock, mock_get_current_user):
    db_session_mock.query().filter().first.return_value = None

    response = client.get("/api/v1/organizations/999", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Organization not found"

def test_get_organization_invalid_id(db_session_mock, mock_get_current_user):
    response = client.get("/api/v1/organizations/abc", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error
