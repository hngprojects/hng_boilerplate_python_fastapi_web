from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organisation import Organisation
from api.v1.services.organisation import organisation_service
from main import app


def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def mock_org():
    """Mock organisation"""
    return Organisation(
        id=str(uuid7()),
        name="Test Company",
    )


def mock_org_users():
    """Mock organisation users"""
    return [mock_get_current_user()]


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


def test_get_organisation_users_success(client, db_session_mock):
    """Test to successfully get organisation users"""

    app.dependency_overrides[user_service.get_current_user] = (
        lambda: mock_get_current_user
    )
    app.dependency_overrides[organisation_service.paginate_users_in_organisation] = (
        lambda: mock_org_users
    )
    app.dependency_overrides[organisation_service.fetch] = lambda: mock_org

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_orgs_user = success_response(
        status_code=200, message="users fetched successfully", data={}
    )
    mock_organisation = mock_org()

    with patch(
        "api.v1.services.organisation.organisation_service.paginate_users_in_organisation",
        return_value=mock_orgs_user,
    ):
        response = client.get(
            f"/api/v1/organisations/{mock_organisation.id}/users",
            headers={"Authorization": "Bearer token"},
        )

        assert response.status_code == 200


def test_create_organisation_unauthorized(client, db_session_mock):
    """Test to get all users in an organisation without authorization"""

    response = client.get(
        "/api/v1/organisations/orgs_id/users",
    )

    assert response.status_code == 401
