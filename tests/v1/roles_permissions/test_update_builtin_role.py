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
from api.v1.schemas.permissions.roles import RoleUpdate
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

def create_mock_role(mock_db_session, role_id, role_name, is_builtin=True):
    role = Role(id=role_id, name=role_name, is_builtin=is_builtin)
    mock_db_session.query(Role).filter_by(id=role_id).first.return_value = role
    return role

@pytest.fixture
def access_token(mock_db_session):
    user_id = str(uuid7())
    create_mock_user(mock_db_session, user_id, is_superadmin=True)
    access_token = user_service.create_access_token(user_id)
    return access_token

def test_update_builtin_role(mock_db_session, access_token):
    role_id = str(uuid7())
    create_mock_role(mock_db_session, role_id, "old_builtin_role", is_builtin=True)

    headers = {"Authorization": f"Bearer {access_token}"}
    role_update = {"name": "new_builtin_role", "is_builtin": True}

    response = client.put(
        f"/api/v1/built-in/roles/{role_id}",
        json=role_update,
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Built-in role new_builtin_role updated successfully"

def test_update_builtin_role_not_found(mock_db_session, access_token):
    non_existent_role_id = str(uuid7())

    mock_db_session.query(Role).filter_by(id=non_existent_role_id).first.return_value = None

    headers = {"Authorization": f"Bearer {access_token}"}
    role_update = {"name": "new_builtin_role", "is_builtin": True}

    response = client.put(
        f"/api/v1/built-in/roles/{non_existent_role_id}",
        json=role_update,
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Role not found"
    

