from unittest.mock import MagicMock
import uuid
import pytest
from fastapi.testclient import TestClient

from api.db.database import get_db
from main import app

client = TestClient(app)

@pytest.fixture
def db_session_mock():
    """Mock the database dependency"""
    db_session = MagicMock()
    yield db_session

@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    """Override the get_db dependency with the mock"""
    def get_db_override():
        yield db_session_mock
    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}

def test_rate_limiting(db_session_mock, mock_send_email):
    """Test registration endpoint rate limiting"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    unique_email = f"rate.limit.{uuid.uuid4()}@gmail.com"
    
    user_template = {
        "password": "strin8Hsg263@",
        "first_name": "string",
        "last_name": "string",
        "email": unique_email,
        "confirm_password": "strin8Hsg263@"
    }

    headers = {"X-Forwarded-For": "192.168.123.132"}

    # Send 5 successful requests
    for _ in range(5):
        response = client.post("/api/v1/auth/register", json=user_template, headers=headers)
        assert response.status_code == 201

    # Sixth request should be blocked
    response = client.post("/api/v1/auth/register", json=user_template, headers=headers)
    assert response.status_code == 429
    assert "too many requests" in response.json().get("message", "").lower()
