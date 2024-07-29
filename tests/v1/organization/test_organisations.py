import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app
from datetime import datetime
from api.v1.models.organization import Organization
from api.v1.services.user import UserService
from api.db.database import get_db
from unittest.mock import MagicMock, patch

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

    app.dependency_overrides = {}

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    db = MagicMock()
    return db

@pytest.fixture
def mock_get_current_user():
    """Fixture to mock the current user retrieval."""
    with patch.object(UserService, 'get_current_user', return_value={"id": 1, "email": "test@example.com"}):
        yield

def test_get_organization_success(db_session_mock, mock_get_current_user):
    mock_organization = MagicMock(spec=Organization)
    mock_organization.id = 1
    mock_organization.name = "Mock Org 1"
    mock_organization.description = "A test organization"
    mock_organization.created_at = datetime(2023, 1, 1, 12, 0)
    mock_organization.updated_at = datetime(2023, 6, 1, 12, 0)

    db_session_mock.query().filter().first.return_value = mock_organization

    with patch("api.v1.routes.organisations.get_db", return_value=db_session_mock):
        response = client.get("/api/v1/organisations/1", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Mock Org 1"
        assert data["description"] == "A test organization"

def test_get_organization_not_found(db_session_mock, mock_get_current_user):
    db_session_mock.query().filter().first.return_value = None

    with patch("api.v1.routes.organisations.get_db", return_value=db_session_mock):
        response = client.get("/api/v1/organisations/999", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Organization not found"

        
def test_get_organization_invalid_id(db_session_mock, mock_get_current_user):
    response = client.get("/api/v1/organisations/abc", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error