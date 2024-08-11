from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.squeeze import Squeeze
from api.v1.services.squeeze import squeeze_service
from main import app


def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_squeeze():
    return Squeeze(
        id=str(uuid7()),
        title="TTest qustion?",
        email="user2@example.com",
        body="Hello squeeze",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
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


def test_delete_squeeze_success(client, db_session_mock):
    '''Test to successfully delete a new squeeze'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    app.dependency_overrides[squeeze_service.delete] = lambda: None

    # Mock squeeze creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    squeeze = mock_squeeze()

    with patch("api.v1.services.squeeze.squeeze_service.delete", return_value=squeeze) as mock_delete:
        response = client.delete(
            f'/api/v1/squeeze/{squeeze.id}',
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 204


def test_delete_squeeze_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''

    squeeze = mock_squeeze()

    response = client.delete(
        f'/api/v1/squeeze/{squeeze.id}',
        headers={'Authorization': 'Bearer token'},
    )

    assert response.status_code == 401

