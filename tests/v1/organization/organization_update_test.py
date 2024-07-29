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

def test_update_organization_success(client, db_session_mock):
    '''Test to successfully update an existing organization'''

    org_id = "existing-org-id"
    current_user = mock_get_current_user()  # Get the actual user object
    app.dependency_overrides[user_service.get_current_user] = lambda: current_user

    # Mock the organization fetch and user role retrieval
    organization_service.fetch = MagicMock(return_value=mock_org())
    organization_service.get_organization_user_role = MagicMock(return_value='admin')

    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    response = client.patch(
        f'/api/v1/organizations/{org_id}',
        headers={'Authorization': 'Bearer token'},
        json={
            "company_name": "Updated Organization",
            "company_email": "updated@gmail.com",
            "industry": "Tech",
            "organization_type": "Tech",
            "country": "Nigeria",
            "state": "Lagos",
            "address": "Ikorodu, Lagos",
            "lga": "Ikorodu"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == 'Organization updated successfully'
    assert response.json()["data"]["company_name"] == "Updated Organization"

def test_update_organization_missing_field(client, db_session_mock):
    '''Test to fail updating an organization due to missing fields'''

    org_id = "existing-org-id"
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()

    response = client.patch(
        f'/api/v1/organizations/{org_id}',
        headers={'Authorization': 'Bearer token'},
        json={
            "company_email": "updated@gmail.com",
            "industry": "Tech",
            "organization_type": "Tech",
            "country": "Nigeria",
            "state": "Lagos",
        }
    )

    assert response.status_code == 422

def test_update_organization_unauthorized(client, db_session_mock):
    '''Test to fail updating an organization due to unauthorized access'''

    org_id = "existing-org-id"
    response = client.patch(
        f'/api/v1/organizations/{org_id}',
        json={
            "company_name": "Updated Organization",
            "company_email": "updated@gmail.com",
            "industry": "Tech",
            "organization_type": "Tech",
            "country": "Nigeria",
            "state": "Lagos",
            "address": "Ikorodu, Lagos",
            "lga": "Ikorodu"
        }
    )

    assert response.status_code == 401
