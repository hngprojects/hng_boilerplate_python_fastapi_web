import sys
import os
import warnings
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from uuid_extensions import uuid7
from unittest.mock import MagicMock
from api.v1.services.user import user_service
from main import app
from api.v1.models.user import User
from api.v1.models.permissions.role import Role
from api.v1.services.permissions.role_service import role_service
from api.db.database import get_db
from fastapi import HTTPException

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


def create_mock_role(mock_db_session, role_name, org_id):
    role_id = str(uuid7())
    role = Role(id=role_id, name=role_name)
    mock_db_session.query(
        Role
    ).join.return_value.filter.return_value.all.return_value = [role]
    return role


@pytest.fixture
def access_token(mock_db_session):
    user_id = str(uuid7())
    create_mock_user(mock_db_session, user_id, is_superadmin=True)
    access_token = user_service.create_access_token(user_id)
    return access_token


def test_get_roles_for_organisation_success(mock_db_session, access_token):
    """Test fetching roles for a specific organisation successfully."""

    org_id = str(uuid7())
    role_name = "TestRole"
    create_mock_role(mock_db_session, role_name, org_id)

    response = client.get(
        f"/api/v1/organisations/{org_id}/roles",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200


def test_get_roles_for_organisation_not_found(mock_db_session, access_token):
    """Test fetching roles for a non-existing organisation."""

    org_id = str(uuid7())
    mock_db_session.query(
        Role
    ).join.return_value.filter.return_value.all.return_value = []

    response = client.get(
        f"/api/v1/organisations/{org_id}/roles",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Roles not found for the given organisation"


def test_get_roles_for_organisation_unauthorized(mock_db_session):
    """Test unauthorized access to fetching roles for an organisation."""

    org_id = str(uuid7())

    response = client.get(f"/api/v1/organisations/{org_id}/roles")

    assert response.status_code == 401
    assert response.json().get("message") == "Not authenticated"
