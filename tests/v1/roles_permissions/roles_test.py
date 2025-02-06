import sys, os
import warnings
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from uuid_extensions import uuid7
from api.v1.services.user import user_service
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from api.v1.schemas.permissions.permissions import PermissionCreate
from api.v1.schemas.permissions.roles import RoleDeleteResponse
from api.utils.success_response import success_response


warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app
from api.v1.models.user import User
from api.v1.models.permissions.permissions import Permission
from api.v1.models.permissions.role import Role
from api.v1.services.permissions.role_service import role_service
from api.v1.services.permissions.permison_service import permission_service
from api.db.database import get_db

CREATE_PERMISSIONS_ENDPOINT = '/api/v1/permissions'

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_role_service():
    with patch("api.v1.services.permissions.role_service.permission_service", autospec=True) as mock_service:
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
    mock_permission = Permission(
        id=permision_id,
        name=name
    )
    mock_db_session.query(Permission).filter_by(id=permision_id).first.return_value = mock_permission
    return mock_permission

def create_mock_role(mock_db_session, role_name):
    role = Role(id=str(uuid7()), name=role_name)
    mock_db_session.add(role)
    mock_db_session.commit()

@pytest.fixture
def access_token(mock_db_session):
    user_email = "mike@example.com"
    user_id = str(uuid7())
    create_mock_user(mock_db_session, user_id)
    access_token = user_service.create_access_token(user_email)
    return access_token

def test_create_role_success(mock_db_session):
    """Test the successful creation of a role."""

    user_email = "mike@example.com"
    create_mock_user(mock_db_session, user_email)

    access_token = user_service.create_access_token(str(user_email))
    mock_db_session.execute.return_value.fetchall.return_value = []

    role_name = "TestRole"
    role_data = {"name": role_name, "description": "testing role permissions"}

    # Mock role creation
    response = client.post("/api/v1/custom/roles", json=role_data, headers={'Authorization': f'Bearer {access_token}'})
    print("ROLE JSON", response.json())
    assert response.status_code == 201
    assert response.json()["message"] == "Role TestRole created successfully"

def test_delete_role_success(mock_db_session, access_token):
    role_id = "test-role-id"
    response_data = {
        "success": True,
        "status_code": 200,
        "message": "Role successfully deleted.",
        "data": {"id": role_id}
    }

    # Mock the delete_role method
    role_service.delete_role = MagicMock(return_value=response_data)

    response = client.delete(f"/api/v1/roles/{role_id}", headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 200
    assert response.json() == response_data
    role_service.delete_role.assert_called_once_with(mock_db_session, role_id)

    
    
    

def test_delete_role_unexpected_error(mock_db_session, access_token):
    role_id = "test-role-id"

    # Mock the delete_role method to raise an unexpected exception
    role_service.delete_role = MagicMock(side_effect=HTTPException(status_code=500, detail="An unexpected error occurred"))

    response = client.delete(f"/api/v1/roles/{role_id}", headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 500
    assert response.json() == {
        "message": "An unexpected error occurred",
        "status": False,
        "status_code": 500
    }
    role_service.delete_role.assert_called_once_with(mock_db_session, role_id)


def test_delete_role_not_found(mock_db_session, access_token):
    role_id = "non-existent-role-id"

    # Mock the delete_role method to raise an HTTPException
    role_service.delete_role = MagicMock(side_effect=HTTPException(status_code=404, detail="Role not found"))

    response = client.delete(f"/api/v1/roles/{role_id}", headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 404
    assert response.json() == {
        "message": "Role not found",
        "status": False,
        "status_code": 404
    }
    role_service.delete_role.assert_called_once_with(mock_db_session, role_id)
