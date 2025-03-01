from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from fastapi import status
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organisation import Organisation

from main import app


def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def mock_org():
    """Mock organisation"""
    return Organisation(
        id=str(uuid7()),
        name="Test Company",
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


def test_remove_user_from_organisation_success(client, db_session_mock):
    """Test to successfully remove a user from an organisation by an admin"""

    admin_user = mock_get_current_admin()
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: admin_user

    with patch(
        "api.v1.services.organisation.organisation_service.get_organisation_by_id"
    ) as mock_remove:
        mock_remove.return_value = success_response(
            status_code=status.HTTP_200_OK,
            message="User successfully removed from organisation",
        )

        org_id = str(uuid7())
        user_id = str(uuid7())

        response = client.delete(
            f"/api/v1/organisations/{org_id}/users/{user_id}",
            headers={"Authorization": "Bearer admin_token"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "User successfully removed from organisation",
            "success": True,
            "status_code": 200,
        }
        mock_remove.assert_called_once()


def test_remove_user_from_organisation_failure(client, db_session_mock):
    """Test when the user is not in the organisation by an admin"""

    admin_user = mock_get_current_admin()
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: admin_user

    # Simulate that the user is not found in the organisation
    db_session_mock.execute.return_value.fetchone.return_value = None

    org_id = str(uuid7())
    user_id = str(uuid7())

    response = client.delete(
        f"/api/v1/organisations/{org_id}/users/{user_id}",
        headers={"Authorization": "Bearer admin_token"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["message"] == "User is not part of this organisation"
