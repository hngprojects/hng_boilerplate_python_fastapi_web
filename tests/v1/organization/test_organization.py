from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organization import Organization
from api.v1.services.user import UserService
from api.v1.services.organization import organization_service
from main import app

client = TestClient(app)

def mock_org():
    return Organization(
        id=str(uuid7()),
        company_name="Test Organization",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
)
# Create a mock database session
@pytest.fixture
def db_session_mock():
    db = MagicMock()
    yield db
    db.close()

# Override the get_db dependency
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def _get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

# Mock the current user function
@pytest.fixture
def mock_get_current_user():
    with patch.object(UserService, 'get_current_user', return_value={"id": 1, "email": "test@example.com"}):
        yield

    db_session_mock.query().filter().first.return_value = mock_org

def test_get_organization_invalid_id(db_session_mock, mock_get_current_user):
    response = client.get("/api/v1/organizations/abc", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error
