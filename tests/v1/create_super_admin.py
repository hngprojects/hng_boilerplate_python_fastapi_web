import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from uuid_extensions import uuid7
from fastapi import HTTPException

from main import app
from api.v1.routes.superadmin import get_db
from api.v1.services.user import user_service
from api.v1.schemas.user import UserCreate, UserBase
from api.v1.models.user import User  # Adjust this import based on your actual model

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

def test_create_super_user_success(client, db_session_mock):
    user_id = uuid7()
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)
    created_at = timeinfo
    updated_at = timeinfo

    # Create a mock user object
    user = User(
        id=user_id,
        username="string06",
        email="string06@example.com",
        password="String06",  # assuming password is hashed
        first_name="string",
        last_name="string06!",
        is_active=True,
        is_super_admin=True,
        is_deleted=False,
        is_verified=True,
        created_at=created_at,
        updated_at=updated_at
    )

    # Mock the user_service.create method to return the mock user
    with patch.object(user_service, 'create', return_value=user):
        response = client.post(
            "/api/v1/superadmin/register",
            json={
                "username": "string06",
                "password": "String06!",
                "first_name": "string",
                "last_name": "string06!",
                "email": "string06@example.com"
            }
        )

    # Assert the response
    assert response.status_code == 201
    jsonResp = response.json()

    resp = {
            "id": jsonResp["data"]["id"],
            "username": jsonResp["data"]["username"],
            "first_name": jsonResp["data"]["first_name"],
            "last_name": jsonResp["data"]["last_name"],
            "email": jsonResp["data"]["email"],

    }
    assert resp == {
            "id": str(user_id),
            "username": "string06",
            "first_name": "string",
            "last_name": "string06!",
            "email": "string06@example.com",
        }
    
def test_create_super_user_already_exists(client, db_session_mock):
    # Configure the mock to raise an exception if the user already exists
    with patch.object(user_service, 'create', side_effect=HTTPException(status_code=400, detail='User with this email or username already exists')):
        response = client.post(
            "/api/v1/superadmin/register",
            json={
                "first_name": "Marvelous",
                "last_name": "Uboh",
                "username": "marveld0",
                "password": "Doyinsola174@$",
                "email": "marveld0@example.com"
            }
        )
    
    # Assert the response
    assert response.status_code == 400
    assert response.json()["message"] == "User with this email or username already exists"

def test_create_super_user_missing_field(client, db_session_mock):
    response = client.post(
        "/api/v1/superadmin/register",
        json={
            "first_name": "Marvelous",
            "last_name": "Uboh",
            "username": "marveld0",
            "password": "Doyinsola174@$"
            # Missing email
        }
    )
    
    # Assert the response
    assert response.status_code == 422
    assert "message" in response.json()  # Check that validation error is returned
