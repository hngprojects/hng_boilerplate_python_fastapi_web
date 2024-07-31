import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.v1.services.contact_us import contact_us_service
from api.v1.models.user import User
from main import app
from sqlalchemy.orm import Session
from api.v1.services.user import user_service
from api.db.database import get_db
from api.v1.services.user import oauth2_scheme

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

def mock_deps():
    return MagicMock(id="user_id")

def mock_db():
    return MagicMock(spec=Session)

def mock_oauth():
    return 'access_token'

class TestCodeUnderTest:

    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = mock_deps
        app.dependency_overrides[get_db] = mock_db


    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Successfully retrieves all contact-us submissions
    def test_retrieve_contact_us_success(self, client, mocker):
        mock_db = MagicMock()
        mock_submissions = [{"full_name": 'Chi', "email": "test@example.com",
                             "title": "Dr", "message": "Fix Up"},
                            {"full_name": 'Me', "email": "test1@example.com",
                             "title": "Engr", "message": "Fix down"}]

        mocker.patch.object(contact_us_service, 'fetch_all', return_value=mock_submissions)

        response = client.get('/api/v1/contact')

        assert response.status_code == 200
        assert response.json()['success'] == True
        assert response.json()['message'] == "Submissions retrieved successfully"
        assert len(response.json()['data']) == len(mock_submissions)

    # No contact-us submissions in the database
    
    def test_retrieve_contact_us_no_submissions(self, client, mocker):
        mock_submissions = []

        mocker.patch.object(contact_us_service, 'fetch_all', return_value=mock_submissions)

        response = client.get('/api/v1/contact')

        assert response.status_code == 200
        assert response.json()['success'] == True
        assert response.json()['message'] == "Submissions retrieved successfully"


    # # Unauthorized access to the endpoint    
    def test_retrieve_contact_unauthorized(self, client):
        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = mock_db
        app.dependency_overrides[oauth2_scheme] = mock_oauth

        with patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_super_admin=False)) as cu:

            response = client.get('/api/v1/contact')

            assert response.status_code == 403
            assert response.json()['success'] == False
            assert response.json()['message'] == 'You do not have permission to access this resource'

    # # Unauthenticated access to the endpoint    
    def test_retrieve_contact_unauthenticated(self, client):
        app.dependency_overrides = {}

        response = client.get('/api/v1/contact')

        assert response.status_code == 401
        assert response.json()['success'] == False
        assert response.json()['message'] == 'Not authenticated'
        