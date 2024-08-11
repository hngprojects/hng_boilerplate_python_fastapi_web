import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from datetime import datetime, timezone
from unittest.mock import patch
from unittest import mock


from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.privacy import PrivacyPolicy
from api.v1.schemas.privacy_policies import PrivacyPolicyUpdate
# from api.v1.services.privacy_policies import privacy_service
from main import app


client = TestClient(app)


# Mock the database session dependency
@pytest.fixture
def mock_db_session(mocker=mock):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock


@pytest.fixture
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

@pytest.fixture
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

@pytest.fixture
def mock_privacy():
    return PrivacyPolicy(
        id=str(uuid7()),
        content="this is our privacy policy",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


# hey
def test_update_privacy_policy_success(mock_db_session, mock_privacy, mock_get_current_admin):
    """Test to successfully update an existing privacy policy"""

    # Mock the user service to return the current admin user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin

    # Mock privacy policy retrieval and update
    mock_privacy_policy = mock_privacy
    updated_content = "this is our updated privacy policy"

    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_privacy_policy
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = mock_privacy_policy

    update_data = PrivacyPolicyUpdate(content=updated_content)
    mock_privacy_policy.content = updated_content

    with patch("api.v1.services.privacy_policies.privacy_service.update", return_value=mock_privacy_policy) as mock_update:
        response = client.patch(
            f'/api/v1/privacy-policy/{mock_privacy_policy.id}',
            json=update_data.model_dump(),
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 200
        assert response.json()['data']['content'] == updated_content
        mock_update.assert_called_once_with(mock_db_session, mock_privacy_policy.id, update_data)
