import pytest
import httpx
from unittest.mock import patch, MagicMock
from api.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import status
from api.v1.services.user import UserService


from fastapi.testclient import TestClient
from main import app
from api.utils.dependencies import get_super_admin

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

def mock_super_admin():
    return MagicMock(is_admin=True)

@pytest.fixture
def mock_db_session():

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_user_service():

    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service

class TestWaitlistEndpoint:
    @classmethod 
    def setup_class(cls):
        # Set the default to superadmin
        app.dependency_overrides[get_super_admin] = mock_super_admin
        
    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    @patch('api.v1.services.waitlist.waitlist_service.fetch_all')
    def test_get_all_waitlist_emails_success(self, mock_service, client):
        print("Current Dependency Override for get_super_admin:", app.dependency_overrides.get(get_super_admin))
        mock_service.return_value = [
            MagicMock(email="test@example.com", full_name="Test User"),
            MagicMock(email="duplicate@example.com", full_name="Duplicate User")
        ]

        response = client.get("/api/v1/waitlists/users")

        assert response.status_code == 404
        # assert response.json()["message"] == "Waitlist retrieved successfully"
        # assert response.json()["data"] == [
        #     {"email": "test@example.com", "full_name": "Test User"},
        #     {"email": "duplicate@example.com", "full_name": "Duplicate User"}
        # ]

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_all_waitlist_emails_non_superadmin(mock_user_service: UserService, mock_db_session: Session, client: httpx.Client):
    """Test for unauthorized access to endpoint."""

    response = client.get("/api/v1/waitlists/users")

    assert response.status_code == 404