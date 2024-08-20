from uuid_extensions import uuid7
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.permissions.permissions import Permission
from api.v1.models.permissions.role import Role
from api.v1.models.user import User
from api.v1.services.user import user_service
from main import app

# Helper functions to create mock data
def mock_role():
    return Role(
        id=str(uuid7()),
        name="Test Role",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_permission():
    return Permission(
        id=str(uuid7()),
        title="Test Permission",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_superuser():
    return User(
        id=str(uuid7()),
        email="superuser@example.com",
        password="hashedpassword",
        first_name="Super",
        last_name="User",
        is_active=True,
        is_superadmin=True,
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

def test_update_role_permission_success(client, db_session_mock):
    """Test updating a role's permission successfully"""

    role = mock_role()
    old_permission = mock_permission()
    new_permission = mock_permission()
    superuser = mock_superuser()

    # Mock the role, permissions, and superuser
    db_session_mock.query(Role).filter_by(id=role.id).first.return_value = role
    db_session_mock.query(Permission).filter_by(id=old_permission.id).first.return_value = old_permission
    db_session_mock.query(Permission).filter_by(id=new_permission.id).first.return_value = new_permission
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: superuser

    # Mock the update function
    db_session_mock.commit.return_value = None

    response = client.put(
        f"/api/v1/roles/{role.id}/permissions/{old_permission.id}",
        json={"new_permission_id": new_permission.id},
        headers={'Authorization': 'Bearer token'}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Permission updated successfully"

def test_update_role_permission_not_found(client, db_session_mock):
    """Test updating a role's permission when the role or permissions are not found"""

    role_id = str(uuid7())
    old_permission_id = str(uuid7())
    new_permission_id = str(uuid7())
    superuser = mock_superuser()

    # Simulate role or permissions not found
    db_session_mock.query(Role).filter_by(id=role_id).first.return_value = None
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: superuser

    response = client.put(
        f"/api/v1/roles/{role_id}/permissions/{old_permission_id}",
        json={"new_permission_id": new_permission_id},
        headers={'Authorization': 'Bearer token'}
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Role not found."

def test_update_role_permission_invalid_permission(client, db_session_mock):
    """Test updating a role's permission with an invalid new permission ID"""

    role = mock_role()
    old_permission = mock_permission()
    superuser = mock_superuser()
    new_perission = mock_permission()

    # Mock the role and old permission
    db_session_mock.query(Role).filter_by(id=role.id).first.return_value = role
    db_session_mock.query(Permission).filter_by(id=old_permission.id).first.return_value = old_permission

    # Simulate new permission not found
    db_session_mock.query(Permission).filter_by(id=new_perission.id).first.return_value = None
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: superuser

    response = client.put(
        f"/api/v1/roles/{role.id}/permissions/{old_permission.id}",
        json={"new_permission_id": new_perission.id},
        headers={'Authorization': 'Bearer token'}
    )

    assert response.status_code == 404