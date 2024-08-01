from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from uuid import uuid4
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organization import Organization
from api.v1.services.user import UserService
from api.v1.services.organization import organization_service
from main import app



# Mock user
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

# Mock organization
def mock_org():
    return Organization(
        id=str(uuid7()),
        company_name="Test Organization",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
)
    
# Fixture for the TestClient
@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: MagicMock(spec=Session)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# Fixture to mock the database session
@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

# Override the get_db dependency
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def _get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()
    
@pytest.fixture
def mock_get_current_user():
    with patch.object(UserService, 'get_current_user', return_value={"id": 1, "email": "test@example.com"}):
        yield

def test_get_organization_success(client, db_session_mock, mock_get_current_user):
    mock_organization = Organization(
        id=str(uuid4()),
        company_name="Test Organization",
        company_email="testorg@gmail.com",
        industry="Tech",
        organization_type="Tech",
        country="Nigeria",
        state="Lagos",
        address="123 Street",
        lga="LGA",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db_session_mock.query().filter().first.return_value = mock_organization

    response = client.get(f"/api/v1/organizations/{mock_organization.id}", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert response.json()["message"] == 'Retrieved organization successfully'
    assert response.json()["data"]["company_name"] == "Updated Organization"

def test_get_organization_not_found(client, db_session_mock, mock_get_current_user):
    db_session_mock.query().filter().first.return_value = None

    response = client.get("/api/v1/organizations/nonexistent-id", headers={"Authorization": "Bearer token"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Organization not found"

def test_get_organization_invalid_id(client, db_session_mock, mock_get_current_user):
    response = client.get("/api/v1/organizations/invalid-id", headers={"Authorization": "Bearer token"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error