import sys
import os
import warnings
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from uuid_extensions import uuid7
from api.v1.services.user import user_service
from fastapi import HTTPException

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from main import app
from api.v1.models.user import User
from api.v1.models.role import Role
from api.v1.services.role import role_service
from api.db.database import get_db

client = TestClient(app)


@pytest.fixture
def mock_db_session(mocker):
    mock_db = mocker.patch("api.db.database.get_db", autospec=True)
    app.dependency_overrides[get_db] = lambda: mock_db
    yield mock_db
    app.dependency_overrides = {}


def create_mock_user(mock_db_session, user_id):
    mock_user = User(
        id=user_id,
        email="testuser@gmail.com",
        password="hashed_password",
        first_name="Test",
        last_name="User",
        is_active=True,
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
    user_email = "mike@example.com"
    user_id = str(uuid7())
    create_mock_user(mock_db_session, user_id)
    access_token = user_service.create_access_token(user_email)
    return access_token


def test_get_roles_for_organization_success(mock_db_session, access_token):
    """Test fetching roles for a specific organization successfully."""

    org_id = str(uuid7())
    role_name = "TestRole"
    create_mock_role(mock_db_session, role_name, org_id)

    response = client.get(
        f"/api/v1/organizations/{org_id}/roles",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == role_name


def test_get_roles_for_organization_not_found(mock_db_session, access_token):
    """Test fetching roles for a non-existing organization."""

    org_id = str(uuid7())
    mock_db_session.query(
        Role
    ).join.return_value.filter.return_value.all.return_value = []

    response = client.get(
        f"/api/v1/organizations/{org_id}/roles",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Roles not found for the given organization"


def test_get_roles_for_organization_unauthorized(mock_db_session):
    """Test unauthorized access to fetching roles for an organization."""

    org_id = str(uuid7())

    response = client.get(f"/api/v1/organizations/{org_id}/roles")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
