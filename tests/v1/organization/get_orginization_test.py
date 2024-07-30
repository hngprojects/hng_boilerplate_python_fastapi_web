import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.models.organization import Organization
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone

client = TestClient(app)
USERORG_ENDPOINT = '/organizations/'

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.v1.services.organization.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""
    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service

def create_mock_user(mock_user_service, mock_db_session, is_super_admin=False):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=is_super_admin,
        is_deleted=False,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

def create_mock_organizations(mock_db_session, user_id):
    """Create a list of mock organizations."""
    mock_orgs = [
        Organization(
            id=str(uuid7()),
            name=f"Test Organization {i}",
            description=f"Description for org {i}",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        for i in range(3)
    ]
    mock_db_session.query.return_value.filter.return_value.all.return_value = mock_orgs
    return mock_orgs

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_user_organizations(mock_user_service, mock_db_session):
    """Test for retrieving user organizations."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=mock_user.id)

    # Mock the `get_current_user` method to return the mock user
    mock_user_service.get_current_user.return_value = mock_user

    mock_orgs = create_mock_organizations(mock_db_session, mock_user.id)

    response = client.get(USERORG_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status_code'] == status.HTTP_200_OK
    assert response.json()['message'] == "Organizations retrieved successfully"
    assert len(response.json()['data']) == len(mock_orgs)
    for org, resp_org in zip(mock_orgs, response.json()['data']):
        assert resp_org['name'] == org.name
        assert resp_org['description'] == org.description
