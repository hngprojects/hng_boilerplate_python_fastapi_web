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

def mock_org():
    return Organization(
        id=str(uuid7()),
        company_name="Test Organization",
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
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.v1.services.id.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_get_current_user():
    with patch.object(UserService, 'get_current_user', return_value={"id": 1, "email": "test@example.com"}):
        yield
        
@pytest.fixture
def override_get_db():
    # This will be our "mock" database session
    db = MagicMock()

    # Setting up the mock to return the mock data
    def mock_query(organization_id):
        org = next((org for org in mock_org if org.id == organization_id), None)
        if org is None:
            return None
        return MagicMock(first=MagicMock(return_value=org))

    # Mocking the session's query method
    db.query.return_value.filter.return_value = MagicMock()
    db.query.return_value.filter.return_value.first = lambda: mock_query(db.query.return_value.filter.return_value.filter_by_args[0])

    try:
        yield db
    finally:
        db.close()

# Use the override_get_db fixture to replace the get_db dependency
@pytest.fixture(autouse=True)
def set_up(monkeypatch):
    monkeypatch.setattr("api.v1.routes.organization.get_db", override_get_db)


def test_get_organization_success(db_session_mock, mock_get_current_user):
    
    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user
    app.dependency_overrides[organization_service.fetch] = lambda: mock_org

    # Mock organization creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_organization = MagicMock(spec=Organization)
    mock_organization.id = 1
    mock_organization.company_name = "Mock Org 1"
    mock_organization.company_email = "contact@mockorg1.com"
    mock_organization.industry = "Technology"
    mock_organization.organization_type = "Private"
    mock_organization.country = "Country"
    mock_organization.state = "State"
    mock_organization.address = "123 Street"
    mock_organization.lga = "LGA"

    db_session_mock.query().filter().first.return_value = mock_organization

    with patch("api.v1.routes.organization.get_db", autospec=True) as mock_get_db:
        response = client.get("/api/v1/organizations/1", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["status_code"] == 200
        assert data["data"]["id"] == 1
        assert data["data"]["company_name"] == "Mock Org 1"
        assert data["data"]["company_email"] == "contact@mockorg1.com"


def test_get_organization_not_found(db_session_mock, mock_get_current_user):
    db_session_mock.query().filter().first.return_value = None

    with patch("api.v1.routes.organization.get_db", autospec=True) as mock_get_db:
        response = client.get("/api/v1/organizations/999", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 404
        data = response.json()
        assert data["message"] == "Organization not found"
        assert data["status_code"] == 404
        assert data["success"] is False

def test_get_organization_invalid_id(db_session_mock, mock_get_current_user):
    response = client.get("/api/v1/organizations/abc", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error
