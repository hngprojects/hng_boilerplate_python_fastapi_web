import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app
from datetime import datetime
from api.v1.models.organization import Organization
from api.v1.services.user import UserService
from api.db.database import get_db
from unittest.mock import MagicMock, patch


from datetime import datetime, timezone
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.services.organization import organization_service

client = TestClient(app)

# Mock current user
def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

# Mock organization object
def mock_org():
    return Organization(
        id=str(uuid7()),
        company_name="Test Organization",
        company_email="testorg@example.com",
        industry="Tech",
        organization_type="Private",
        country="Country",
        state="State",
        address="Address",
        lga="LGA",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
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

    db_session_mock.query().filter().first.return_value = mock_organization

    with patch("api.v1.routes.organization.get_db", return_value=db_session_mock):
        response = client.get("/api/v1/organizations/1", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Mock Org 1"
        assert data["description"] == "A test organization"

def test_get_organization_not_found(db_session_mock, mock_get_current_user):
    db_session_mock.query().filter().first.return_value = None

    with patch("api.v1.routes.organization.get_db", return_value=db_session_mock):
        response = client.get("/api/v1/organizations/999", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 404
        data = response.json()
        assert "message" in data
        assert data["message"] == "Organization not found"
        assert "status_code" in data
        assert data["status_code"] == 404
        assert "success" in data
        assert data["success"] is False

def test_get_organization_invalid_id(db_session_mock, mock_get_current_user):
    response = client.get("/api/v1/organizations/abc", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error