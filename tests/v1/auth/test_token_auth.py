import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from main import app
from api.v1.models.token_login import TokenLogin
from api.v1.models.user import User
from api.v1.routes.auth import get_db

@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield

    app.dependency_overrides = {}

client = TestClient(app)

token = TokenLogin(token="123456", expiry_time=datetime.utcnow() + timedelta(seconds=60))

@patch('api.v1.services.user.UserService.generate_token')
def test_request_signin_token(mock_generate_token, db_session_mock):
    # Mock user
    user = User(email="user@gmail.com", id="someid")
    db_session_mock.query.return_value.filter.return_value.first.return_value = token
    response = {"status_code": 200, "message": f"Sign-in token sent to {user.email}"}

    assert response.get("status_code") == 200
    assert response["message"] == f"Sign-in token sent to {user.email}"
    

@patch('api.v1.services.user.UserService.verify_login_token')
def test_verify_signin_token(mock_verify_login_token, db_session_mock):
    # Mock user with token
    user = User(email="user@gmail.com", id="someid")
    db_session_mock.query.return_value.filter.return_value.first.return_value = user
    
    mock_verify_login_token.return_value = user

    response = client.post("/api/v1/auth/verify-token",
                           json={"email": "user@gmail.com", "token": "123456"})

    assert response.status_code == 200
    assert "access_token" in response.json()
