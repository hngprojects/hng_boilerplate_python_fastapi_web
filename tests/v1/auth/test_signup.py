import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from api.db.database import get_db
from api.v1.models.newsletter import Newsletter
from api.v1.models.user import User
from slowapi.errors import RateLimitExceeded
import uuid
import time

client = TestClient(app)

# Mock the database dependency
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield

    app.dependency_overrides = {}

def test_status_code(db_session_mock, mock_send_email):
    db_session_mock.query(Newsletter).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    user = {
        "password": "strin8Hsg263@",
        "first_name": "string",
        "last_name": "string",
        "email": "user@gmail.com"
    }

    response = client.post("/api/v1/auth/register", json=user)

    assert response.status_code == 201
    # mock_send_email.assert_called_once()

def test_user_fields(db_session_mock, mock_send_email):

    db_session_mock.query(Newsletter).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    user = {
        "password": "strin8Hsg263@",
        "first_name": "sunday",
        "last_name": "mba",
        "email": "mba@gmail.com"
    }

    response = client.post("/api/v1/auth/register", json=user)

    assert response.status_code == 201
    assert response.json()['data']["user"]['email'] == "mba@gmail.com"
    assert response.json()['data']["user"]['first_name'] == "sunday"
    assert response.json()['data']["user"]['last_name'] == "mba"
    # mock_send_email.assert_called_once()
    
def test_rate_limiting(db_session_mock):
    db_session_mock.query(User).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    
    unique_email = f"rate.limit.{uuid.uuid4()}@gmail.com"
    user = {
        "password": "ValidP@ssw0rd!",
        "first_name": "Rate",
        "last_name": "Limit",
        "email": unique_email
    }


    response = client.post("/api/v1/auth/register", json=user)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
    
    time.sleep(5)  # Adjust this delay to see if it prevents rate limiting

    for _ in range(5):
        response = client.post("/api/v1/auth/register", json=user)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"