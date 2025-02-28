import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from api.v1.models.user import User
from api.v1.routes.auth import get_db
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from datetime import datetime, timezone

client = TestClient(app)

@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}

@pytest.fixture(autouse=True)
def override_get_current_user():
    """Mock user with all required fields."""
    mock_user = User(
        id="123456",
        email="testuser1@gmail.com",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_deleted=False,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides = {}

def test_get_current_user():
    """Test for retrieving current user details."""
    headers = {"Authorization": "Bearer fake_token"}
    response = client.get("/api/v1/auth/@me", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    
    assert response_json["data"]["user"]["email"] == "testuser1@gmail.com"
    assert response_json["data"]["user"]["first_name"] == "Test"
    assert response_json["data"]["user"]["last_name"] == "User"
