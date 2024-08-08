import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from api.v1.models.newsletter import NewsletterSubscriber
from unittest.mock import MagicMock
from api.v1.services.user import oauth2_scheme, user_service

def mock_deps():
    return MagicMock(id="user_id")

def mock_oauth():
    return 'access_token'

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

class TestUnsubscribeNewsletter:

    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = mock_deps

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_unsubscribe_success(self, db_session_mock):
        # Arrange
        existing_subscriber = NewsletterSubscriber(email="test@example.com")
        db_session_mock.query(NewsletterSubscriber).filter().first.return_value = existing_subscriber

        email_data = {"email": "test@example.com"}

        # Act
        response = client.post("/api/v1/pages/newsletters/unsubscribe", json=email_data)

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == "Unsubscribed successfully."

    def test_unsubscribe_email_not_found(self, db_session_mock):
        # Arrange
        db_session_mock.query(NewsletterSubscriber).filter().first.return_value = None

        email_data = {"email": "notfound@example.com"}

        # Act
        response = client.post("/api/v1/pages/newsletters/unsubscribe", json=email_data)

        # Assert
        assert response.status_code == 404
        assert response.json()["message"] == "Email not found."

if __name__ == "__main__":
    pytest.main()
