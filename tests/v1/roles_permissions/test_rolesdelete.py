import sys, os
import warnings
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from uuid_extensions import uuid7
from api.v1.services.user import user_service
from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.permissions.role import Role


client = TestClient(app)

mock_id = str(uuid7())

@pytest.fixture
def mock_db_session():
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


def test_deleteuser(mock_db_session):
    dummy_admin = User (
        id=mock_id,
        email= "Testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Mr",
        last_name="Dummy",
        is_active=True,
        is_super_admin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    app.dependency_overrides[user_service.get_current_super_admin] = lambda : dummy_admin

    dummy_role = Role(
        id = mock_id,
        name='Dummyrolename',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_db_session.query().filter().first.return_value = dummy_role

    delete_role_url = f'api/v1/users/{dummy_role.id}'

    success_response = client.delete(delete_role_url)

    assert success_response.status_code == 204

    """Unauthenticated Users"""

    app.dependency_overrides[user_service.get_current_super_admin] = user_service.get_current_super_admin
    
    delete_role_url = f'api/v1/users/{dummy_role.id}'

    unsuccess_response = client.delete(delete_role_url)

    assert unsuccess_response.status_code == 401



