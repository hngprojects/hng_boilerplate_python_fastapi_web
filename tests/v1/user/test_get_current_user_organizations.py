from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.organisation import Organisation
from api.v1.services.user import user_service
from api.v1.models import User
from main import app


# Mock user with organisations
def mock_get_current_user():
    # Create mock organisations
    org1 = Organisation(id=str(uuid7()), name="Organisation One")
    org2 = Organisation(id=str(uuid7()), name="Organisation Two")

    # Create mock user
    mock_user = User(
        id=str(uuid7()),
        email="user@gmail.com",
        password=user_service.hash_password("Testuser@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        organisations=[org1, org2]
    )
    return mock_user


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


def test_get_user_organisations_unauthorized(client, db_session_mock):
    '''Test unauthorized response'''

    response = client.get(
        '/api/v1/users/organisations',
    )

    assert response.status_code == 401