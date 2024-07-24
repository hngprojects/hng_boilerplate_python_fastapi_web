import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.org import Organization
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone

client = TestClient(app)
DELETE_ORGANIZATION_ENDPOINT = '/superadmin/organizations/{org_id}'

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        mock_organization = create_mock_organization(mock_db)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_organization
        mock_db.delete = MagicMock()
        mock_db.commit = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_organization_service():
    """Fixture to create a mock organization service."""
    with patch("api.v1.services.organization.delete", autospec=True) as mock_service:
        yield mock_service

@pytest.fixture
def mock_user_superadmin():
    """Fixture to mock superadmin user."""
    with patch("api.v1.services.user.get_current_user") as mock_get_current_user:
        mock_get_current_user.return_value = {"id": 1, "role": "superadmin"}
        yield mock_get_current_user

@pytest.fixture
def mock_user_normal():
    """Fixture to mock normal user."""
    with patch("api.v1.services.user.get_current_user") as mock_get_current_user:
        mock_get_current_user.return_value = {"id": 2, "role": "normal"}
        yield mock_get_current_user

def create_mock_organization(mock_db_session):
    """Create and add a mock organization to the mock database session."""
    mock_organization = Organization(
        id=str(uuid7()),
        name="Test Organization",
        description="A test organization",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    if not hasattr(mock_db_session, 'organizations'):
        mock_db_session.organizations = []
    mock_db_session.organizations.append(mock_organization)
    mock_db_session.query.return_value.filter.return_value.first.side_effect = lambda: next(
        (org for org in mock_db_session.organizations if org.id == mock_organization.id), None
    )
    return mock_organization

@pytest.mark.usefixtures("mock_db_session", "mock_organization_service")
def test_delete_organization_success(mock_organization_service, mock_db_session):
    """Test for successful organization deletion."""
    mock_organization = create_mock_organization(mock_db_session)
    print(f"Mock Organization ID: {mock_organization.id}")
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_organization
    mock_organization_service.return_value = True

    response = client.delete(DELETE_ORGANIZATION_ENDPOINT.format(org_id=mock_organization.id))
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    expected_response = {
        "status": 200,
        "message": "Organization deleted successfully",
        "data": {}
    }
    assert response.json() == expected_response

    mock_db_session.query.return_value.filter.return_value.first.assert_called_with(mock_organization.id)
    mock_db_session.delete.assert_called_once_with(mock_organization)
    mock_db_session.commit.assert_called_once()

@pytest.mark.usefixtures("mock_db_session", "mock_organization_service")
def test_delete_organization_not_found(mock_organization_service, mock_db_session):
    """Test for organization deletion when organization is not found."""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    response = client.delete(DELETE_ORGANIZATION_ENDPOINT.format(org_id=str(uuid7())))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Not Found"
    }
