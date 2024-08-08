import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from api.v1.models.newsletter import NewsletterSubscriber
from api.v1.schemas.newsletter import EmailSchema
from unittest.mock import patch, MagicMock
from api.v1.services.newsletter import NewsletterService
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

def test_sub_newsletter_success(db_session_mock):
    # Arrange
    db_session_mock.query(NewsletterSubscriber).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    email_data = {"email": "test1@example.com"}

    # Act
    response = client.post("/api/v1/newsletters", json=email_data)

    # Assert
    assert response.status_code == 201


def test_sub_newsletter_existing_email(db_session_mock):
    # Arrange
    existing_subscriber = NewsletterSubscriber(email="test@example.com")
    db_session_mock.query(NewsletterSubscriber).filter().first.return_value = existing_subscriber

    email_data = {"email": "test@example.com"}

    # Act
    response = client.post("/api/v1/newsletters", json=email_data)

    # Assert
    assert response.status_code == 400

class TestCodeUnderTest:

    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = mock_deps


    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Successfully retrieves all subscriptions from db
    def test_retrieve_subscription_success(self, mocker):
        mock_subs= [{"email": "test@example.com"},
                    {"email": "test1@example.com"}]
        mocker.patch.object(NewsletterService, 'fetch_all', return_value=mock_subs)

        response = client.get('/api/v1/newsletters')

        assert response.status_code == 200
        assert response.json()['success'] == True
        assert response.json()['message'] == "Subscriptions retrieved successfully"
        assert len(response.json()['data']) == len(mock_subs)

    # No subscriptions in database
    def test_retrieve_contact_us_no_submissions(self, mocker):
        mock_submissions = []
        app.dependency_overrides[user_service.get_current_super_admin] = mock_deps

        mocker.patch.object(NewsletterService, 'fetch_all', return_value=mock_submissions)

        response = client.get('/api/v1/newsletters')

        assert response.status_code == 200
        assert response.json()['success'] == True
        assert response.json()['message'] == "Subscriptions retrieved successfully"
        assert response.json()['data'] == [{}]


    # # Unauthorized access to the endpoint    
    def test_retrieve_unauthorized(self):
        app.dependency_overrides = {}
        app.dependency_overrides[oauth2_scheme] = mock_oauth

        with patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_super_admin=False)) as cu:

            response = client.get('/api/v1/newsletters')

            assert response.status_code == 403

    # # Unauthenticated access to the endpoint    
    def test_retrieve_contact_unauthenticated(self):
        app.dependency_overrides = {}

        response = client.get('/api/v1/newsletters')

        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main()
