import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from ...main import app
from api.v1.models.org import Organization
from api.v1.models.user import User
from api.v1.routes.user import get_db

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

# Helper function to simulate authenticated requests
def get_authenticated_client(client: TestClient, token: str):
    response = client.get("/api/v1/organizations/current-user", headers={"Authorization": f"Bearer {token}"})
    return response

def test_get_organizations_for_current_user_empty(client, db_session_mock):
    # Mock the return value for the query
    db_session_mock.query().filter().all.return_value = []

    # Mock the return value for the current user with a valid token
    token = "valid_token"
    db_session_mock.query(User).filter().first.return_value = User(id=uuid7())

    # Call the endpoint with authentication
    response = get_authenticated_client(client, token)

    # Assert the response
    assert response.status_code == 200
    assert response.json() == []

def test_get_organizations_for_current_user_with_data(client, db_session_mock):
    # Define UUIDs and timestamps
    user_id = uuid7()
    org_id = uuid7()
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)

    # Create a mock user
    user = User(
        id=user_id,
        username="testuser",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        created_at=timeinfo
    )

    # Create a mock organization
    organization = Organization(
        id=org_id,
        name="Test Organization",
        description="Test Description"
    )

    # Associate the organization with the user
    user.organizations = [organization]

    # Mock the return value for the user query
    token = "valid_token"
    db_session_mock.query(User).filter().first.return_value = user

    # Call the endpoint with authentication
    response = get_authenticated_client(client, token)

    # Assert the response
    assert response.status_code == 200
    assert response.json() == [{
        "org_id": str(org_id),
        "org_slug": None,  # Assuming `org_slug` is not part of the mock model
        "name": "Test Organization",
        "description": "Test Description"
    }]

def test_get_organizations_without_authentication(client):
    # Call the endpoint without authentication
    response = client.get("/api/v1/organizations/current-user")

    # Assert the response
    assert response.status_code == 401
    assert response.json() == {
        "status_code": 401,
        "message": "User not authenticated"
    }

def test_get_organizations_server_error(client, db_session_mock):
    # Simulate a server error
    db_session_mock.query().filter().all.side_effect = Exception("Database error")

    # Mock the return value for the current user
    token = "valid_token"
    db_session_mock.query(User).filter().first.return_value = User(id=uuid7())

    # Call the endpoint with authentication
    response = get_authenticated_client(client, token)

    # Assert the response
    assert response.status_code == 500
    assert response.json() == {
        "status_code": 500,
        "message": "Internal server error"
    }
