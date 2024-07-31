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

client = TestClient(app)

# Mock data
MOCK_ORGANIZATIONS = [
    Organization(id=1, name="Mock Org 1", description="A test organization", created_at="2023-01-01T12:00:00Z", updated_at="2023-06-01T12:00:00Z"),
    Organization(id=2, name="Mock Org 2", description="Another test organization", created_at="2023-02-01T12:00:00Z", updated_at="2023-07-01T12:00:00Z"),
]

@pytest.fixture
def override_get_db():
    # This will be our "mock" database session
    db = MagicMock()

    # Setting up the mock to return the mock data
    def mock_query(organization_id):
        org = next((org for org in MOCK_ORGANIZATIONS if org.id == organization_id), None)
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

def test_get_organization_success():
    response = client.get("/api/v1/organizations/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Mock Org 1"
    assert data["description"] == "A test organization"

def test_get_organization_not_found():
    response = client.get("/api/v1/organizations/999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Organization not found"

def test_get_organization_invalid_id():
    response = client.get("/api/v1/organizations/abc")
    assert response.status_code == 422  # Unprocessable Entity due to validation error