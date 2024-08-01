import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError


from fastapi.testclient import TestClient
from main import app
from api.utils.dependencies import get_super_admin

def mock_deps():
    return MagicMock(is_admin=True)

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

class TestCodeUnderTest:
    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[get_super_admin] = mock_deps
        
    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Successfully adding a user to the waitlist with valid email and full name
    
    @patch('api.v1.routes.waitlist.find_existing_user')
    def test_add_user_to_waitlist_success(self, mock_service, client):
        
        app.dependency_overrides[get_super_admin] = mock_deps

        mock_service.return_value = None
        
        response = client.post("/api/v1/waitlist/admin", json={"email": "test@example.com", "full_name": "Here"})

        assert response.status_code == 201
        assert response.json()["message"] == "User added to waitlist successfully"

    # # Handling empty full_name field and raising appropriate exception
    def test_add_user_to_waitlist_empty_full_name(self, mocker, client):
        app.dependency_overrides[get_super_admin] = mock_deps

        response = client.post("/api/v1/waitlist/admin", json={"email": "test@example.com", "full_name": ""})
    
        assert response.status_code == 400
        assert response.json()["message"] == "full_name field cannot be blank"

    # # Handling invalid email format and raising appropriate exception
    def test_add_user_to_waitlist_invalid_email(self, client):    
        response = client.post("/api/v1/waitlist/admin", json={"email": "invalid-email", "full_name": "Test User"})
    
        assert response.status_code == 422

    # # Handling duplicate email entries and raising IntegrityError
    @patch('api.v1.routes.waitlist.find_existing_user')
    def test_add_user_to_waitlist_duplicate_email(self, mock_service, client):

        client = TestClient(app)
    
        # Simulate IntegrityError when adding duplicate email
        response = client.post("/api/v1/waitlist/admin", json={"email": "duplicate@example.com", "full_name": "Test User"})
    
        assert response.status_code == 400
        assert response.json()["message"]== "Email already added"
