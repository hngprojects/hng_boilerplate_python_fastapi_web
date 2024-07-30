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
from api.v1.services.organization import organization_service
from main import app

# Mock function to simulate getting the current user
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

# Mock function to simulate fetching an organization
def mock_org():
    return Organization(
        id=str(uuid7()),
        company_name="Test Organization",
        company_email="info@testorg.com",
        industry="Technology",
        organization_type="Private",
        country="Nigeria",
        state="Lagos",
        address="123 Tech Street",
        lga="Ikeja",
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
def mock_current_user():
    return mock_get_current_user()

def test_get_organization_success(client, db_session_mock, mock_current_user):
    '''Test to successfully retrieve an organization by ID'''

    app.dependency_overrides[user_service.get_current_user] = lambda: mock_current_user
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_org()

    response = client.get(
        f'/api/v1/organizations/{mock_org().id}',
        headers={'Authorization': 'Bearer token'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Test Organization"
    assert data["company_email"] == "info@testorg.com"
    assert data["industry"] == "Technology"
    assert data["organization_type"] == "Private"
    assert data["country"] == "Nigeria"
    assert data["state"] == "Lagos"
    assert data["address"] == "123 Tech Street"
    assert data["lga"] == "Ikeja"


def test_get_organization_not_found(client, db_session_mock, mock_current_user):
    '''Test retrieving an organization that does not exist'''
    
    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_current_user
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    org_id = str(uuid7())
    response = client.get(
        f'/api/v1/organizations/{org_id}',
        headers={'Authorization': 'Bearer token'},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Organization not found"

def test_get_organization_invalid_id(client):
    '''Test retrieving an organization with an invalid ID format'''

    invalid_org_id = "invalid_id"  # Use a non-UUID string

    response = client.get(
        f'/api/v1/organizations/{invalid_org_id}',
        headers={'Authorization': 'Bearer token'},
    )

    assert response.status_code == 422  # Unprocessable Entity due to validation error
