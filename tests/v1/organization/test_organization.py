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
    return MagicMock(spec=Session)

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    yield TestClient(app)
    app.dependency_overrides = {}

@pytest.fixture
def mock_get_current_user_fixture():
    with patch("api.v1.routes.organization.get_db", return_value=mock_get_current_user()) as mock:
        yield mock

def test_get_organization_success(client, db_session_mock, mock_get_current_user_fixture):
    '''Test to successfully retrieve an organization by ID'''

    org_id = str(uuid7())  # Use a UUID for the org_id
    mock_organization = mock_org()
    mock_organization.id = org_id  # Set the ID to match

    # Mock the organization fetch
    with patch("api.v1.routes.organization.get_db", return_value=mock_organization):
        response = client.get(
            f'/api/v1/organizations/{org_id}',
            headers={'Authorization': 'Bearer token'},
        )

    assert response.status_code == 200
    assert response.json()["message"] == 'Retrieve Organization successfully'
    assert response.json()["data"]["company_name"] == "Test Organization"

def test_get_organization_not_found(client, db_session_mock, mock_get_current_user_fixture):
    '''Test retrieving an organization that does not exist'''

    org_id = str(uuid7())  # Use a UUID for the org_id

    # Mock the organization fetch to return None
    with patch("api.v1.routes.organization.get_db", return_value=None):
        response = client.get(
            f'/api/v1/organizations/{org_id}',
            headers={'Authorization': 'Bearer token'},
        )

    assert response.status_code == 404
    assert response.json()["message"] == "Organization not found"

def test_get_organization_invalid_id(client, db_session_mock, mock_get_current_user_fixture):
    '''Test retrieving an organization with an invalid ID format'''

    invalid_org_id = "invalid_id"  # Use a non-UUID string

    response = client.get(
        f'/api/v1/organizations/{invalid_org_id}',
        headers={'Authorization': 'Bearer token'},
    )

    assert response.status_code == 422  # Unprocessable Entity due to validation error
