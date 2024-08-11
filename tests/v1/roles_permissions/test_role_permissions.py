import sys
import os
import warnings
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.models.permissions.role import Role
from api.v1.models.permissions.permissions import Permission
from api.v1.models.permissions.role_permissions import role_permissions
from api.db.database import get_db
from uuid_extensions import uuid7
from main import app

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

client = TestClient(app)

@pytest.fixture
def mock_db_session(mocker):
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    yield mock_db
    app.dependency_overrides = {}

def create_mock_user(mock_db_session, user_id, is_superadmin=False):
    mock_user = User(
        id=user_id,
        email="testuser@gmail.com",
        password="hashed_password",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superadmin=is_superadmin,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db_session.query(User).filter_by(id=user_id).first.return_value = mock_user
    return mock_user

def create_mock_role(mock_db_session, role_name):
    role_id = str(uuid7())
    role = Role(id=role_id, name=role_name)
    mock_db_session.query(
        Role
    ).filter_by(id=role_id).first.return_value = role
    return role

@pytest.fixture
def access_token(mock_db_session):
    user_id = str(uuid7())
    create_mock_user(mock_db_session, user_id, is_superadmin=True)
    access_token = user_service.create_access_token(user_id)
    return access_token

@pytest.fixture
def create_permissions(mock_db_session):
    permissions = [
        Permission(id=str(uuid7()), title="perm_1"),
        Permission(id=str(uuid7()), title="perm_2")
    ]
    mock_db_session.query(Permission).all.return_value = permissions
    return permissions

@pytest.fixture
def create_role(mock_db_session):
    return create_mock_role(mock_db_session, "test_role")

def test_update_role_permissions(mock_db_session, access_token, create_permissions):
    # Simulate login
    create_user = create_mock_user(mock_db_session, str(uuid7()), is_superadmin=True)
    create_role = create_mock_role(mock_db_session, "test_role")
    permission_ids = [perm.id for perm in create_permissions]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.put(
        f"/api/v1/roles/{create_role.id}/permissions/{permission_ids[0]}",
        json={"new_permission_id": permission_ids[1]},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == "Permission updated successfully"

def test_update_role_permissions_role_not_found(mock_db_session, access_token, create_permissions):
    # Simulate login
    create_user = create_mock_user(mock_db_session, str(uuid7()), is_superadmin=True)
    permission_ids = [perm.id for perm in create_permissions]

    non_existent_role_id = str(uuid7())
    mock_db_session.query(Role).filter_by(id=non_existent_role_id).first.return_value = None

    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.put(
        f"/api/v1/roles/{non_existent_role_id}/permissions/{permission_ids[0]}",
        json={"new_permission_id": permission_ids[1]},
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Role not found."



def test_update_role_permissions_unauthorized(mock_db_session, create_role, create_permissions):
    permission_ids = [perm.id for perm in create_permissions]

    response = client.put(
        f"/api/v1/roles/{create_role.id}/permissions/{permission_ids[0]}",
        json={"new_permission_id": permission_ids[1]}
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Not authenticated"
