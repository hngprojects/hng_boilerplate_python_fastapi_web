import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from api.db.database import get_db
from api.v1.models.newsletter import Newsletter

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

def test_status_code(db_session_mock):
    db_session_mock.query(Newsletter).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    user = {
        "username": "string",
        "password": "strin8Hsg263@",
        "first_name": "string",
        "last_name": "string",
        "email": "user@example.com"
    }

    response = client.post("/api/v1/auth/register", json=user)

    assert response.status_code == 201

def test_user_fields(db_session_mock):

    db_session_mock.query(Newsletter).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    user = {
        "username": "mba",
        "password": "strin8Hsg263@",
        "first_name": "sunday",
        "last_name": "mba",
        "email": "mba@gmail.com"
    }

    response = client.post("/api/v1/auth/register", json=user)

    assert response.status_code == 201
    assert response.json()['data']["user"]['email'] == "mba@gmail.com"
    assert response.json()['data']["user"]['username'] == "mba"
    assert response.json()['data']["user"]['first_name'] == "sunday"
    assert response.json()['data']["user"]['last_name'] == "mba"