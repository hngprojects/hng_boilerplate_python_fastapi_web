import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from ...main import app
from api.v1.models import Organization, User
# from api.v1.routes.organization import get_db
from api.db.database import get_db


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

def test_get_user_organizations_success(client, db_session_mock):
    # Mock the user and their organizations
    user_id = uuid4()
    org_id = uuid4()
    org_name = "Test Organization"
    org_description = "Test Description"
    
    organization = Organization(
        id=org_id,
        name=org_name,
        description=org_description
    )
    
    user = User(
        id=user_id,
        organizations=[organization]
    )
    
    # Mock the return value for the user retrieval
    db_session_mock.query().filter().first.return_value = user

    # Call the endpoint with a valid Authorization header
    response = client.get("/api/v1/organizations/current-user", headers={"Authorization": "Bearer valid_token"})

    # Assert the response
    assert response.status_code == 200
    assert response.json() == [{
        "id": str(org_id),
        "name": org_name,
        "description": org_description
    }]

def test_get_user_organizations_no_credentials(client, db_session_mock):
    # Call the endpoint without credentials
    response = client.get("/api/v1/organizations/current-user")

    # Assert the response
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_get_user_organizations_server_error(client, db_session_mock):
    # Mock the user retrieval to raise an exception
    db_session_mock.query().filter().first.side_effect = Exception("Database error")

    # Call the endpoint with a valid Authorization header
    response = client.get("/api/v1/organizations/current-user", headers={"Authorization": "Bearer valid_token"})

    # Assert the response
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
