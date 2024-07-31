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

def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_org():
    return Organization(
        id=1,  # Ensure this ID is an integer to match the route parameter type
        company_name="Test Organization",
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
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}

@pytest.fixture
def mock_get_current_user_fixture():
    with patch.object(UserService, 'get_current_user', return_value=mock_get_current_user()):
        yield

def test_get_organization_success(client, db_session_mock, mock_get_current_user_fixture):
    # Mock organization service to return a mock organization
    mock_organization = mock_org()
    db_session_mock.query().filter().first.return_value = mock_organization

    response = client.get("/api/v1/organizations/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["status_code"] == 200
    assert data["data"]["id"] == 1
    assert data["data"]["company_name"] == "Mock Org 1"
    assert data["data"]["company_email"] == "contact@mockorg1.com"

def test_get_organization_not_found(client, db_session_mock, mock_get_current_user_fixture):
    db_session_mock.query().filter().first.return_value = None

    response = client.get("/api/v1/organizations/999", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 404
    data = response.json()
    assert data["message"] == "Organization not found"
    assert data["status_code"] == 404
    assert data["success"] is False

def test_get_organization_invalid_id(client, mock_get_current_user_fixture):
    response = client.get("/api/v1/organizations/abc", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error
    data = response.json()
    assert "errors" in data
    assert data["errors"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"
