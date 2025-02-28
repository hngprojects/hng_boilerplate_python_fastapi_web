from unittest.mock import MagicMock
import uuid

import pytest
from fastapi.testclient import TestClient

from api.db.database import get_db
from main import app

client = TestClient(app)

# Mock the database dependency
@pytest.fixture
def db_session_mock():
    """Mock the database dependency"""
    db_session = MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    """Override the get_db dependency with the mock"""
    def get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = get_db_override
    yield

    app.dependency_overrides = {}

def test_rate_limiting(db_session_mock, mock_send_email, mocker):
    """Test registration endpoint rate limiting with IP mocking"""
    # Mock database operations
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    # Mock IP address for all requests
    mock_client = mocker.patch("fastapi.Request.client")
    mock_client.host = "192.168.123.132"
   
    unique_email = f"rate.limit.{uuid.uuid4()}@gmail.com"

    user_template = {
        "password": "strin8Hsg263@",
        "first_name": "string",
        "last_name": "string",
        "email": unique_email
    }

    # First 5 requests from same IP
    for _ in range(5):
        mock_client = mocker.patch("fastapi.Request.client")
        mock_client.host = "192.168.123.132"
        response = client.post("/api/v1/auth/register", json=user_template)
        assert response.status_code == 201

    # Sixth request from same IP should be blocked
    response = client.post("/api/v1/auth/register", json=user_template)
    assert response.status_code == 429
    assert "Too many requests" in response.json()["message"]
