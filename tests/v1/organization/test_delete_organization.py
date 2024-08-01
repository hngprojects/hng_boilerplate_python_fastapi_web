from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from datetime import datetime, timezone

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organization import Organization
from main import app


def mock_get_db():
    db_session = MagicMock()
    yield db_session


def mock_get_current_super_admin():
    return User(id="1", is_super_admin=True)

def mock_get_current_normal_user():
    return User(id="1", is_super_admin=False)

@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session


@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client


def test_delete_organization_owner(client, db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    app.dependency_overrides[user_service.get_current_user] = mock_get_current_super_admin

    org_id = uuid7()
    mock_organization = Organization(
        id=org_id,
        company_name="Test Organization",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db_session_mock.query(Organization).filter(id == org_id).first.return_value.id = [
        mock_organization
    ]

    response = client.delete(f"/api/v1/organizations/{mock_organization.id}", headers={'Authorization': 'Bearer token'})

    assert response.status_code == 204


def test_non_admin_can_delete_organization(client, db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    app.dependency_overrides[user_service.get_current_user] = mock_get_current_normal_user

    org_id = uuid7()
    mock_organization = Organization(
        id=org_id,
        company_name="Test Organization",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db_session_mock.query(Organization).filter(id == org_id).first.return_value.id = [
        mock_organization
    ]

    response = client.delete(f"/api/v1/organizations/{mock_organization.id}", headers={'Authorization': 'Bearer token'})

    assert response.status_code == 403