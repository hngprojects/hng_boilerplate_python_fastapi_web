from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.privacy import PrivacyPolicy
from api.v1.services.privacy_policies import privacy_service
from main import app


def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


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


def mock_privacy():
    return PrivacyPolicy(
        id=str(uuid7()),
        content="this is our privacy policy",
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

def test_delete_privacy_policy_success(client, db_session_mock):
    '''Test to successfully delete an existing privacy policy'''

    # Mock the user service to return the current admin user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin

    # Mock privacy policy retrieval and deletion
    mock_privacy_policy = mock_privacy()
    db_session_mock.query.return_value.filter_by.return_value.first.return_value = mock_privacy_policy
    db_session_mock.delete.return_value = None
    db_session_mock.commit.return_value = None

    with patch("api.v1.services.privacy_policies.privacy_service.delete", return_value=None) as mock_delete:
        response = client.delete(
            f'/api/v1/privacy-policy/{mock_privacy_policy.id}',
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 204
        mock_delete.assert_called_once_with(db_session_mock, mock_privacy_policy.id)
