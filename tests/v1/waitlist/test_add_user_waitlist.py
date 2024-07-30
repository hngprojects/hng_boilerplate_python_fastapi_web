# Dependencies:
# pip install pytest-mock
import pytest
import httpx
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from api.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import status
from api.v1.services.user import user_service, UserService


from fastapi.testclient import TestClient
from main import app
from api.utils.dependencies import get_super_admin

def mock_deps():
    return MagicMock(is_admin=True)

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

@pytest.fixture
def mock_db_session():

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        # mock_get_db.return_value.__enter__.return_value = mock_db
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_user_service():

    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service

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
        
        response = client.post("/api/v1/waitlists/admin", json={"email": "test@example.com", "full_name": "Here"})

        assert response.status_code == 201
        assert response.json()["message"] == "User added to waitlist successfully"

    # # Handling empty full_name field and raising appropriate exception
    def test_add_user_to_waitlist_empty_full_name(self, mocker, client):
        app.dependency_overrides[get_super_admin] = mock_deps

        response = client.post("/api/v1/waitlists/admin", json={"email": "test@example.com", "full_name": ""})
    
        assert response.status_code == 400
        assert response.json()["message"] == "full_name field cannot be blank"

    # # Handling invalid email format and raising appropriate exception
    def test_add_user_to_waitlist_invalid_email(self, client):    
        response = client.post("/api/v1/waitlists/admin", json={"email": "invalid-email", "full_name": "Test User"})
    
        assert response.status_code == 422

    # # Handling duplicate email entries and raising IntegrityError
    @patch('api.v1.routes.waitlist.find_existing_user')
    def test_add_user_to_waitlist_duplicate_email(self, mock_service, client):

        client = TestClient(app)
    
        # Simulate IntegrityError when adding duplicate email
        response = client.post("/api/v1/waitlists/admin", json={"email": "duplicate@example.com", "full_name": "Test User"})
    
        assert response.status_code == 400
        assert response.json()["message"]== "Email already added"

class TestWaitlistEndpoint:
    @classmethod 
    def setup_class(cls):
        # Set the default to superadmin
        app.dependency_overrides[get_super_admin] = mock_deps
        
    @classmethod
    def teardown_class(cls):
        # Clear dependency overrides after tests
        app.dependency_overrides = {}

    @patch('api.v1.services.waitlist.waitlist_service.fetch_all')
    def test_get_all_waitlist_emails_success(self, mock_service, client):
        print("Current Dependency Override for get_super_admin:", app.dependency_overrides.get(get_super_admin))
        # Mock return value for fetch_all method
        mock_service.return_value = [
            MagicMock(email="test@example.com"),
            MagicMock(email="duplicate@example.com")
        ]

        response = client.get("/api/v1/waitlists/users")

        assert response.status_code == 200
        assert response.json()["message"] == "Waitlist retrieved successfully"
        assert response.json()["data"] == ["test@example.com", "duplicate@example.com"]

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_waitlist_emails_non_superadmin(mock_user_service: UserService, mock_db_session: Session, client: httpx.Client):
    """Test for unauthorized access to endpoint."""

    response = client.get("/api/v1/waitlists/users")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED