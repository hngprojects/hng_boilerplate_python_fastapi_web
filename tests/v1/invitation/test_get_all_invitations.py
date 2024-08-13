from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from uuid_extensions import uuid7
from api.v1.models.invitation import Invitation
from api.v1.services.user import user_service, UserService
from main import app
from api.db.database import get_db
from api.v1.models.user import User

client = TestClient(app)
@pytest.fixture
def mock_db_session():
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

def test_get_all_invitations(mock_db_session):
    
    invitations = [Invitation(user_id=str(uuid7()), is_valid = True , organisation_id = str(uuid7()), id=str(uuid7()))]

    mock_db_session.query().all.return_value = invitations

    app.dependency_overrides[user_service.get_current_super_admin] = lambda :  User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashed_password",
        first_name='Test',
        last_name='User',
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_superadmin = True
    )

    res = client.get('/api/v1/organisations/invites')

    assert res.status_code == 200
    
