import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from api.db.database import get_db
from api.v1.models.user import User
import uuid

client = TestClient(app)

@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

@pytest.fixture
def redis_mock():
    redis_client = MagicMock()
    yield redis_client

@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}

# Test normal user registration
def test_register_normal_user(db_session_mock):
    db_session_mock.query(User).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    user = {
        "password": "NormalP@ss123",
        "confirm_password": "NormalP@ss123",
        "first_name": "Normal",
        "last_name": "User",
        "email": "normal.user@gmail.com",
        "is_superadmin": "false"
    }

    response = client.post("/api/v1/auth/register", json=user)
    
    assert response.status_code == 201
    assert response.json()['data']['user']['email'] == "normal.user@gmail.com"
    assert response.json()['data']['user']['is_superadmin'] == "false"

# Test admin registration
def test_register_admin_user(db_session_mock):
    db_session_mock.query(User).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    admin = {
        "password": "AdminP@ss123",
        "confirm_password": "AdminP@ss123",
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin.user@gmail.com",
        "is_superadmin": "true"
    }

    response = client.post("/api/v1/auth/register-super-admin", json=admin)
    
    assert response.status_code == 201
    assert response.json()['data']['user']['email'] == "admin.user@gmail.com"
    assert response.json()['data']['user']['is_superadmin'] == "true"

# Test verify token - valid token
def test_verify_signin_token_success(db_session_mock, redis_mock):
    user = User(email="user@gmail.com", id="someid")
    db_session_mock.query(User).filter().first.return_value = user

    redis_mock.hgetall.return_value = {
        "email": "user@gmail.com",
        "token": "123456",
        "first_name": "John",
        "last_name": "Doe",
        "password": "hashedpassword"
    }

    with patch("api.core.dependencies.redis_cache.get_redis_client", redis_mock):
        token_schema = {"email": "user@gmail.com", "token": "123456"}
        response = client.post("/api/v1/auth/verify-token", json=token_schema)

    assert redis_mock.hgetall.return_value["token"] == token_schema["token"]

# Test verify token - invalid token
def test_verify_signin_token_invalid(db_session_mock, redis_mock):
    redis_mock.hgetall.return_value = {
        "email": "user@gmail.com",
        "token": "654321"
    }

    with patch("api.core.dependencies.redis_cache.get_redis_client", redis_mock):
        token_data = {"email": "user@gmail.com", "token": "123456"}
        response = client.post("/api/v1/auth/verify-token", json=token_data)

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid email or token"

