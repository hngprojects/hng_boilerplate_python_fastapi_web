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
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session


@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_create_organisation_success(client, db_session_mock):
    """Test to successfully create a new organisation"""

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = (
        lambda: mock_get_current_user
    )
    app.dependency_overrides[organisation_service.create] = lambda: mock_org

    # Mock organisation creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_organisation = mock_org()

    with patch(
        "api.v1.services.organisation.organisation_service.create",
        return_value=mock_organisation,
    ) as mock_create:
        response = client.post(
            "/api/v1/organisations",
            headers={"Authorization": "Bearer token"},
            json={
                "name": "Joboy dev",
                "email": "dev@gmail.com",
                "industry": "Tech",
                "type": "Tech",
                "country": "Nigeria",
                "state": "Lagos",
                "address": "Ikorodu, Lagos",
                "description": "Ikorodu",
            },
        )

        assert response.status_code == 201


def test_create_organisation_missing_field(client, db_session_mock):
    """Test for missing field when creating a new organisation"""
    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = (
        lambda: mock_get_current_user
    )
    app.dependency_overrides[organisation_service.create] = lambda: mock_org
    # Mock organisation creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None
    mock_organisation = mock_org()
    with patch(
        "api.v1.services.organisation.organisation_service.create",
        return_value=mock_organisation,
    ) as mock_create:
        response = client.post(
            "/api/v1/organisations",
            headers={"Authorization": "Bearer token"},
            json={
                "email": "dev@gmail.com",
                "industry": "Tech",
                "type": "Tech",
                "country": "Nigeria",
            },
        )
        assert response.status_code == 422


def test_create_organisation_unauthorized(client, db_session_mock):
    """Test for unauthorized user"""

    response = client.post(
        "/api/v1/organisations",
        json={
            "name": "Joboy dev",
            "email": "dev@gmail.com",
            "industry": "Tech",
            "type": "Tech",
            "country": "Nigeria",
            "state": "Lagos",
            "address": "Ikorodu, Lagos",
            "description": "Ikorodu",
        },
    )

    assert response.status_code == 401
