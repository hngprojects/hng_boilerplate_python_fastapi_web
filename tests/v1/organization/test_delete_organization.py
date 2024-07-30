import pytest

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid_extensions import uuid7
from sqlalchemy.orm import Session

from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organization import Organization
# from api.v1.services.organization import organization_service
from main import app


@pytest.fixture(autouse=True)
def client() -> TestClient:
    client = TestClient(app)
    return client

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

user = mock_get_current_user()

@pytest.fixture()
def mock_org():
    return Organization(
        id=str(uuid7()),
        company_name="Test Organization",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        owner=user
    )

@pytest.fixture(autouse=True)
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

access_token = user_service.create_access_token(user.id)
print(access_token)

def test_delete_organization_endpoint_and_response(client, mock_org):
    '''Test for deleting an existing organization endpoint and response'''
    print(f'/api/v1/organizations/{mock_org.id}')
    response = client.delete(f'/api/v1/organizations/{mock_org.id}')

    assert response.status_code == 204

def test_owner_can_delete_organization(client, mock_org):
    '''Test for deleting an organization as owner'''
    pass

def test_response_of_deletion_on_non_existent_organization():
    pass

