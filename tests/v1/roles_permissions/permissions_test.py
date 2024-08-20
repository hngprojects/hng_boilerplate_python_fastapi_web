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
from api.v1.models.permissions.role import Role
from api.v1.services.permissions.permison_service import permission_service
from api.db.database import get_db

CREATE_PERMISSIONS_ENDPOINT = '/api/v1/permissions'

client = TestClient(app)

mock_id = str(uuid7()) 

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


def create_mock_permissions(mock_db_session, title, permision_id):
    mock_permission= Permission(
        id=permision_id,
        title=title
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
        "title" : "Read"
    }

    response = client.post(CREATE_PERMISSIONS_ENDPOINT, json=paylod, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json()['message'] == 'permissions created successfully'


def test_create_permission_endpoint_integrity_error(mock_db_session, mock_permission_service):
    """Test for handling IntegrityError when creating a permission."""
    permission_data = {"title": "Read"}
    user_email = "mike@example.com"
    access_token = user_service.create_access_token(str(user_email))
    mock_db_session.execute.return_value.fetchall.return_value = []
    mock_db_session.add.side_effect = IntegrityError("mock error", {}, None)
    
    headers={'Authorization': f'Bearer {access_token}'}
    response = client.post("/api/v1/permissions", json=permission_data, headers=headers)
    assert response.status_code == 400
    assert response.json()["message"] == "A permission with this title already exists."


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

    # Instead of mocking `add`, mock `commit` to raise the IntegrityError
    mock_db_session.commit.side_effect = IntegrityError("mock error", {}, None)
    
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post(f"api/v1/roles/{role_id}/permissions", json=payload, headers=headers)

    assert response.status_code == 400
    assert response.json()["message"] == "This permission already exists for the role"


def test_deleteuser(mock_db_session):
    dummy_admin = User (
        id=mock_id,
        email= "Testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Mr",
        last_name="Dummy",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    app.dependency_overrides[user_service.get_current_super_admin] = lambda : dummy_admin

    dummy_permission = Permission(
        id = mock_id,
        title='DummyPermissionname',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_db_session.query().filter().first.return_value = dummy_permission

    delete_permission_url = f'api/v1/permissions/{dummy_permission.id}'

    success_response = client.delete(delete_permission_url)

    assert success_response.status_code == 204

    """Unauthenticated Users"""
    
    app.dependency_overrides[user_service.get_current_super_admin] = user_service.get_current_super_admin
    
    delete_permission_url = f'api/v1/permissions/{dummy_permission.id}'

    unsuccess_response = client.delete(delete_permission_url)

    assert unsuccess_response.status_code == 401
