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

# Fixture to mock the database session
@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

# Fixture to set up the test client with dependency overrides
@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

# Test case to verify successful organization retrieval
def test_get_organization_success(client, db_session_mock):
    '''Test to successfully retrieve an existing organization'''
    current_user = mock_get_current_user()
    app.dependency_overrides[user_service.get_current_user] = lambda: current_user

    db_session_mock.query().filter().first.return_value = mock_org()

    response = client.get("/api/v1/organizations/1", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["company_name"] == "Test Organization"
    assert data["company_email"] == "testorg@gmail.com"

# Test case to handle organization not found scenario
def test_get_organization_not_found(client, db_session_mock):
    '''Test to handle organization not found scenario'''
    current_user = mock_get_current_user()
    app.dependency_overrides[user_service.get_current_user] = lambda: current_user

    db_session_mock.query().filter().first.return_value = None

    response = client.get("/api/v1/organizations/999", headers={"Authorization": "Bearer token"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Organization not found"

def test_get_organization_invalid_id(db_session_mock, mock_get_current_user):
    response = client.get("/api/v1/organizations/abc", headers={"Authorization": "Bearer token"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error
