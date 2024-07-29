import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app
from api.v1.models.organization import Organization
from api.v1.services.user import UserService
from api.db.database import get_db
from unittest.mock import MagicMock, patch

client = TestClient(app)

MOCK_ORGANIZATIONS = [
    Organization(id=1, name="Mock Org 1", description="A test organization", created_at="2023-01-01T12:00:00Z", updated_at="2023-06-01T12:00:00Z"),
    Organization(id=2, name="Mock Org 2", description="Another test organization", created_at="2023-02-01T12:00:00Z", updated_at="2023-07-01T12:00:00Z"),
]

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
def override_get_db():
    db = MagicMock()
    
    # Mock query method to return an object with a first method
    def mock_query_filter(organization_id):
        if organization_id == 1:
            return MagicMock(first=MagicMock(return_value=MOCK_ORGANIZATIONS[0]))
        elif organization_id == 999:
            return MagicMock(first=MagicMock(return_value=None))
        else:
            raise HTTPException(status_code=422, detail="Invalid ID format")

    db.query.return_value.filter.return_value = MagicMock()
    db.query.return_value.filter.return_value.first = lambda: mock_query_filter(db.query.return_value.filter.return_value.filter_by_args[0])
    yield db

@pytest.fixture(autouse=True)
def set_up(monkeypatch):
    monkeypatch.setattr("api.v1.routes.organisations.get_db", override_get_db)

@pytest.fixture
def token():
    return "testtoken"  # Mock token

def test_get_organization_success(token):
    with patch.object(UserService, 'get_current_user', return_value={"id": 1, "email": "test@example.com"}):
        response = client.get("/api/v1/organisations/1", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Mock Org 1"
        assert data["description"] == "A test organization"

def test_get_organization_not_found(token):
    with patch.object(UserService, 'get_current_user', return_value={"id": 1, "email": "test@example.com"}):
        response = client.get("/api/v1/organisations/999", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Organization not found"

def test_get_organization_invalid_id(token):
    with patch.object(UserService, 'get_current_user', return_value={"id": 1, "email": "test@example.com"}):
        response = client.get("/api/v1/organisations/abc", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 422  # Unprocessable Entity due to validation error
