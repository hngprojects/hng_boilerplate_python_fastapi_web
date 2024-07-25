import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from uuid import uuid4
from main import app
from api.v1.models.org import Organization
from api.v1.models.user import User
from api.v1.routes.organization import get_db
from api.v1.schemas.user import UserCreate
from api.v1.services.user import user_service
from jose import JWTError
import jwt
from datetime import datetime, timedelta
from .config import SECRET_KEY, ALGORITHM

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

def generate_token(user_id: str, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = {"sub": user_id}
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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

    # Mock valid JWT token
    token = generate_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # Call the endpoint with a valid Authorization header
    response = client.get("/api/v1/organizations/current-user", headers=headers)

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
    assert response.json() == {
        "message": "Not authenticated",
        "status_code": 401,
        "success": False
    }

def test_get_user_organizations_server_error(client, db_session_mock):
    # Mock the user retrieval to raise an exception
    db_session_mock.query().filter().first.side_effect = Exception("Database error")

    # Mock valid JWT token
    token = generate_token(user_id="test_id")
    headers = {"Authorization": f"Bearer {token}"}

    # Call the endpoint with a valid Authorization header
    response = client.get("/api/v1/organizations/current-user", headers=headers)

    # Assert the response
    assert response.status_code == 500
    assert response.json() == {
        "message": "Internal server error",
        "status_code": 500,
        "success": False
    }
