import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from main import app
from datetime import datetime, timezone
from uuid_extensions import uuid7


# Mock database dependency
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

def create_mock_user(mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = User(
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
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    return mock_user

def test_verify_magic_link(client, db_session_mock):
    user = create_mock_user(db_session_mock)
    token = user_service.create_access_token(user_id=user.id)

    response = client.post("/api/v1/auth/magic-link/verify", json={
        "token": token,
    })
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data['message'] == 'Login successful'
    assert data['access_token'] == token

