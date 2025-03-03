import pytest
import time
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid_extensions import uuid7

from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.session import UserSession
from api.v1.services.user import user_service
from api.v1.services.session import session_service



@pytest.fixture
def mock_db():
    mock_db = MagicMock()
    yield mock_db


@pytest.fixture(autouse=True)
def client(mock_db):
    """Override the get_db dependency with the mock."""
    def get_db_override():
        yield mock_db
    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    yield client

@pytest.fixture(autouse=True)
def mock_user():
    """Mock user object."""
    return User(
        id=str(uuid7()),
        email="testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

@pytest.fixture(autouse=True)
def mock_session_1(mock_user):
    """Mock session object."""
    return UserSession(
        id=str(uuid7()),
        user_id=mock_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        ip_address="127.0.0.1",
        location="Lagos, Nigeria",
        device="test-client",
        refresh_token=user_service.create_refresh_token(mock_user.id),
        is_revoked=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture(autouse=True)
def mock_session_2(mock_user):
    time.sleep(1)
    """Mock session object."""
    return UserSession(
        id=str(uuid7()),
        user_id=mock_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        ip_address="127.0.1.1",
        location="Lagos, Nigeria",
        device="test-client-2",
        refresh_token=user_service.create_refresh_token(mock_user.id),
        is_revoked=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

def test_delete_sessions(client, mock_db, mock_user, mock_session_1, mock_session_2):
    """Test deleting all sessions."""
    mock_db.query().filter().all.return_value = [mock_session_1, mock_session_2]
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    response = client.delete(f"/api/v1/sessions/", headers={"Authorization": "Bearer token"})
    
    assert response.status_code == 204
    assert response.json()['message'] == "Sessions deleted successfully"
    assert response.json()['status'] == "success"

def test_delete_session(client, mock_db, mock_user, mock_session_1):
    """Test deleting a session."""
    mock_db.query().filter().first.return_value = mock_session_1
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    response = client.delete(
        f"/api/v1/sessions/{mock_session_1.id}",
        headers={"Authorization": "Bearer token"})
    
    assert response.status_code == 204
    assert response.json()['message'] == "Session deleted successfully"
    assert response.json()['status'] == "success"