"""
Tests for update data privacy settings endpoint
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from main import app
from uuid_extensions import uuid7
from fastapi import status
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.data_privacy import DataPrivacySetting
from api.v1.services.user import user_service, UserService
from api.v1.services.data_privacy import DataPrivacyService, data_privacy_service

client = TestClient(app)
ENDPOINT = "api/v1/settings/data-privacy"


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."

    Yields:
        MagicMock: mock database
    """

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


mock_id = str(uuid7())


@pytest.fixture
def mock_get_current_user():
    """Mock the get_current_user dependency"""

    app.dependency_overrides[user_service.get_current_user] = lambda: User(
        id=mock_id,
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="AdminTest",
        last_name="User",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_update():
    """mock update method"""

    with patch(
        "api.v1.services.data_privacy.DataPrivacyService.update", autospec=True
    ) as mock_update:
        mock_update.return_value = DataPrivacySetting(id=str(uuid7()), user_id=mock_id)

        yield mock_update


SAMPLE_DATA = {
    "profile_visibility": False,
    "allow_analytics": True,
    "personalized_ads": True,
}


def test_unauthorized_access(mock_user_service: UserService, mock_db_session: Session):
    """Test for unauthorized access to endpoint."""

    response = client.patch(f"{ENDPOINT}", json=SAMPLE_DATA)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_succesful_update(
    mock_user_service: UserService,
    mock_db_session: Session,
    mock_get_current_user: None,
    mock_update: None,
):
    """Test for successfull update"""
    response = client.patch(f"{ENDPOINT}", json=SAMPLE_DATA)

    assert response.status_code == status.HTTP_200_OK


def test_invalid_data(
    mock_user_service: UserService,
    mock_db_session: Session,
    mock_get_current_user: None,
):
    """Test for invalid request body"""
    response = client.patch(f"{ENDPOINT}")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
