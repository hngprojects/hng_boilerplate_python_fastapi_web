import sys, os
import warnings
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from uuid_extensions import uuid7
from api.v1.services.user import user_service
from sqlalchemy.exc import IntegrityError
from api.v1.schemas.permissions.permissions import PermissionCreate

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app
from api.v1.models.user import User
from api.v1.models.permissions.permissions import Permission
from api.v1.models.organization import Organization
from api.v1.services.permissions.permison_service import permission_service
from api.db.database import get_db

CREATE_PERMISSIONS_ENDPOINT = '/api/v1/permissions'

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_permission_service():
    with patch("api.v1.services.permissions.permison_service.permission_service", autospec=True) as mock_service:
        yield mock_service

def create_mock_user(mock_db_session, user_id):
    mock_user = User(
        id=user_id,
        email="testuser@gmail.com",
        password="hashed_password",
        first_name='Test',
        last_name='User',
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query(User).filter_by(id=user_id).first.return_value = mock_user
    return mock_user


def create_mock_permissions(mock_db_session, name, permision_id):
    mock_permission= Permission(
        id=permision_id,
        name=name
    )
    mock_db_session.query(Permission).filter_by(id=permision_id).first.return_value = mock_permission
    return mock_permission

def create_mock_role(mock_db_session, role_id):
    mock_role = MagicMock(id=role_id)
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_role
    return mock_role

@pytest.mark.usefixtures("mock_db_session", "mock_permission_service")
def test_create_permission(mock_db_session, mock_permission_service):
    user_email = "mike@example.com"
    create_mock_user(mock_db_session, user_email)

    access_token = user_service.create_access_token(str(user_email))
    mock_db_session.execute.return_value.fetchall.return_value = []

    paylod = {
        "name" : "Read"
    }

    response = client.post(CREATE_PERMISSIONS_ENDPOINT, json=paylod, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json()['name'] == 'Read'


def test_create_permission_endpoint_integrity_error(mock_db_session, mock_permission_service):
    """Test for handling IntegrityError when creating a permission."""
    permission_data = {"name": "Read"}
    user_email = "mike@example.com"
    access_token = user_service.create_access_token(str(user_email))
    mock_db_session.execute.return_value.fetchall.return_value = []
    mock_db_session.add.side_effect = IntegrityError("mock error", {}, None)
    
    headers={'Authorization': f'Bearer {access_token}'}
    response = client.post("/api/v1/permissions", json=permission_data, headers=headers)
    assert response.status_code == 400
    assert response.json()["message"] == "A permission with this name already exists."


@pytest.mark.usefixtures("mock_db_session", "mock_permission_service")
def test_assign_permission_to_role_success(mock_db_session, mock_permission_service):
    """Test for successfully assigning a permission to a role."""

    user_email = "mike@example.com"
    create_mock_user(mock_db_session, user_email)

    access_token = user_service.create_access_token(str(user_email))
    role_id = str(uuid7())
    permission_id = str(uuid7())

    create_mock_permissions(mock_db_session, "Read", permission_id)
    create_mock_role(mock_db_session, role_id)

    mock_db_session.execute.return_value.fetchall.return_value = []

    payload = {
        "permission_id": permission_id
    }

    response = client.post(f"api/v1/roles/{role_id}/permissions", json=payload, headers={'Authorization': f'Bearer {access_token}'})
    print("JSON 1234", response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "Permission assigned successfully"

def test_assign_permission_to_role_invalid_role(mock_db_session, mock_permission_service):
    """Test for assigning a permission to a non-existent role."""

    user_email = "mike@example.com"
    create_mock_user(mock_db_session, user_email)

    access_token = user_service.create_access_token(str(user_email))
    role_id = uuid7
    permission_id = str(uuid7())

    create_mock_permissions(mock_db_session, "Read", permission_id)
    # Do not create the role here to simulate a non-existent role.
    mock_db_session.add.side_effect = IntegrityError("mock error", {}, None)

    payload = {
        "permission_id": permission_id
    }

    response = client.post(f"api/v1/roles/{role_id}/permissions", json=payload, headers={'Authorization': f'Bearer {access_token}'})
    print("JSON 1234", response.json())
    assert response.status_code == 400
    assert response.json()["message"] == "An error occurred while assigning the permission."

def test_assign_permission_to_role_integrity_error(mock_db_session, mock_permission_service):
    """Test for handling IntegrityError when assigning a permission to a role."""

    user_email = "mike@example.com"
    create_mock_user(mock_db_session, user_email)

    access_token = user_service.create_access_token(str(user_email))
    role_id = str(uuid7())
    permission_id = str(uuid7())

    create_mock_permissions(mock_db_session, "Read", permission_id)
    create_mock_role(mock_db_session, role_id)

    payload = {
        "permission_id": permission_id
    }

    mock_db_session.add.side_effect = IntegrityError("mock error", {}, None)
    
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post(f"api/v1/roles/{role_id}/permissions", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.json()["message"] == "An error occurred while assigning the permission."