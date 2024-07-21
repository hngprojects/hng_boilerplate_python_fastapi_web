import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid import uuid4

from main import app
from api.v1.models import * 
from api.utils.dependencies import get_current_user
from api.db.database import get_db

client = TestClient(app)

# Mock data
mock_user = User(id=uuid4(), username="testuser", first_name="Test", last_name="User", email="testuser@example.com", password="password")
mock_org = Organization(id=uuid4(), name="Test Organization", users=[mock_user])

# Mock current user dependency
async def mock_get_current_user():
    return mock_user

# Mock DB dependency
def mock_get_db():
    db_session = MagicMock(spec=Session)
    db_session.query.return_value.filter_by.return_value.first.return_value = mock_org
    return db_session

def mock_get_none():
    db_session = MagicMock(spec=Session)
    db_session.query.return_value.filter_by.return_value.first.return_value = None
    return db_session

@pytest.fixture
def override_get_db():
    app.dependency_overrides[get_db] = mock_get_db
    yield
    app.dependency_overrides[get_db] = get_db

@pytest.fixture
def override_get_none():
    app.dependency_overrides[get_db] = mock_get_none
    yield
    app.dependency_overrides[get_db] = get_db

@pytest.fixture
def override_get_current_user():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides[get_current_user] = get_current_user

@pytest.mark.asyncio
async def test_get_users_success(override_get_db, override_get_current_user):
    response = client.get(f"/api/v1/organization/{mock_org.id}/users")
    assert response.status_code == 200
    assert response.json().get("data") == [user.to_dict() for user in mock_org.users]

@pytest.mark.asyncio
async def test_get_users_org_not_found(override_get_none, override_get_current_user):
    #app.dependency_overrides[get_db] = lambda: MagicMock(spec=Session)
    response = client.get(f"/api/v1/organization/{uuid4()}/users")
    assert response.status_code == 404
    assert response.json().get("message") == "Organization does not exist"

@pytest.mark.asyncio
async def test_get_users_user_not_in_org(override_get_db):
    other_user = User(id=uuid4(), username="otheruser", first_name="Other", last_name="User", email="otheruser@example.com", password="password")
    app.dependency_overrides[get_current_user] = lambda: other_user  # User not in organization
    response = client.get(f"/api/v1/organization/{mock_org.id}/users")
    assert response.status_code == 403
    assert response.json().get("message") == "User does not have access to the organization"

@pytest.mark.asyncio
async def test_get_users_invalid_org_id(override_get_db, override_get_current_user):
    response = client.get("/api/v1/organization/invalid-uuid/users")
    assert response.status_code == 400
    assert response.json() == {"detail": 'Id is not a valid uuid'}

@pytest.mark.asyncio
async def test_get_users_user_not_logged_in(override_get_db):
    app.dependency_overrides[get_current_user] = lambda: None  # No user logged in
    response = client.get(f"/api/v1/organization/{mock_org.id}/users")
    assert response.status_code == 401
    assert response.json() == {"detail": "User is not logged in"}
