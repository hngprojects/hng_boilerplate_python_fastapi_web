import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone


client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""

    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service


def create_mock_user(mock_user_service, mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )
    return mock_user


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_update_billing_plan(mock_user_service, mock_db_session):
    """Billing plan update test."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    data = {
        "name": "Advanced",
        "organisation_id": "s2334d",
        "description": "All you need in one pack",
        "price": 80,
        "duration": "monthly",
        "currency": "Naira",
        "features": ["Multiple team", "Premium support"],
    }

    response = client.patch(
        "/api/v1/organisations/billing-plans/123-1221-090",
        headers={"Authorization": f"Bearer {access_token}"},
        json=data,
    )

    print(response.json())

    assert response.status_code == status.HTTP_200_OK
