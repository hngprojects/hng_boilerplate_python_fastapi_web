# tests/v1/organization/test_organization.py

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organization import Organization
from main import app

def mock_get_current_user():
    return User(
        id=str(uuid4()),
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
        id=1,  # Ensure this ID is an integer if the API expects an integer
        company_name="Test Organization",
        company_email="testorg@example.com",
        industry="Tech",
        organization_type="Private",
        country="Nigeria",
        state="Lagos",
        address="123 Street, Lagos",
        lga="Ikorodu",
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

def test_get_organization_success(client, db_session_mock):
    '''Test to successfully retrieve an organization by ID'''

    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user

    mock_organization = mock_org()
    db_session_mock.query().filter().first.return_value = mock_organization

    response = client.get(
        f'/api/v1/organizations/{mock_organization.id}',
        headers={'Authorization': 'Bearer token'}
    )

    # Validate status code and response content
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert data["status_code"] == 200
    assert data["data"]["id"] == mock_organization.id
    assert data["data"]["company_name"] == mock_organization.company_name

def test_get_organization_not_found(client, db_session_mock):
    '''Test retrieving an organization that does not exist'''

    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user

    db_session_mock.query().filter().first.return_value = None

    response = client.get(
        '/api/v1/organizations/99999',
        headers={'Authorization': 'Bearer token'}
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["message"] == "Organization not found"
    assert data["status_code"] == 404

def test_get_organization_invalid_id(client):
    '''Test retrieving an organization with an invalid ID format'''

    response = client.get(
        '/api/v1/organizations/invalid-id-format',
        headers={'Authorization': 'Bearer token'}
    )

    # Check for status code and validation error format
    assert response.status_code == 422, response.text  # Unprocessable Entity due to validation error
    data = response.json()
    assert "errors" in data
    assert data["errors"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"
