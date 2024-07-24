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
from api.v1.schemas.newsletter import EMAILSCHEMA

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
    # Clean up after the test by removing the override
    app.dependency_overrides = {}

def test_sub_newsletter_success(db_session_mock):
    # Arrange
    db_session_mock.query(Newsletter).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    email_data = {"email": "test1@example.com"}

    # Act
    response = client.post("/api/v1/newsletters", json=email_data)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Thank you for subscribing to our newsletter.",
        "success": True,
        "status": 201
    }

def test_sub_newsletter_existing_email(db_session_mock):
    # Arrange
    existing_subscriber = Newsletter(email="test@example.com")
    db_session_mock.query(Newsletter).filter().first.return_value = existing_subscriber

    email_data = {"email": "test@example.com"}

    # Act
    response = client.post("/api/v1/newsletters", json=email_data)

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        'message': 'Email already exists',
        'status_code': 400,
        'success': False
    }


if __name__ == "__main__":
    pytest.main()
