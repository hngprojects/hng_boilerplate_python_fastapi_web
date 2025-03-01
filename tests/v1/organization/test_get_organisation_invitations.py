from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from api.db.database import get_db
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
    return Organisation(
        id=str(uuid7()),
        name="Test Organisation",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session


def test_get_organisations_invitations_success(client, db_session_mock):
    """
    Test to successfully get organisation invites
    """
    app.dependency_overrides[user_service.get_current_user] = mock_get_current_user

    with patch(
        "api.v1.services.organisation.organisation_service.fetch_all_invitations"
    ) as mock_fetch_all_invitations:
        mock_invitations = [
            {
                "id": str(uuid7()),
                "user_id": str(uuid7()),
                "organisation_id": str(uuid7()),
                "expires_at": datetime.now(timezone.utc),
            }
        ]
        mock_fetch_all_invitations.return_value = (mock_invitations, 1)

        response = client.get("/api/v1/organisations/invites")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "Invites fetched successfully"
        assert "invitations" in response_data["data"]
        assert response_data["data"]["total_count"] == 1
        assert response_data["data"]["page"] == 1
        assert response_data["data"]["page_size"] == 10


def test_get_organisations_invitations_failure(client, db_session_mock):
    """
    Test failure to get organisation invites
    """
    app.dependency_overrides[user_service.get_current_user] = mock_get_current_user

    with patch(
        "api.v1.services.organisation.organisation_service.fetch_all_invitations"
    ) as mock_fetch_all_invitations:
        mock_fetch_all_invitations.side_effect = Exception("An error occurred")

        response = client.get("/api/v1/organisations/invites")
        assert response.status_code == 400
        response_data = response.json()
        assert (
            response_data["message"]
            == "Unable to retrieve organisation invites: An error occurred"
        )
        assert response_data["status_code"] == 400
