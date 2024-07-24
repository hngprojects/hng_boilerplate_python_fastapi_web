import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from datetime import datetime, timezone
import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import UserService
from api.v1.models.job import Job

client = TestClient(app)
user_service = UserService()
JOB_ENDPOINT = '/api/v1/jobs'
LOGIN_ENDPOINT = 'api/v1/auth/login'

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""
    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service

def create_mock_user(mock_user_service, mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=str(uuid7()),
        username="testuser",
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_admin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

def create_mock_job(mock_db_session, user_id):
    """Create a mock job in the mock database session."""
    mock_job = Job(
        id=str(uuid7()), 
        user_id=user_id,
        title="Test Job",
        description="Test Description",
        location="Test Location",
        salary=2000.0,
        job_type="Full-time",
        company_name="Test Company",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_job
    return mock_job

@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_get_job(mock_user_service, mock_db_session):
    """Test for retrieving a job by ID."""
    
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_job = create_mock_job(mock_db_session, mock_user.id)
    
    # Create a token for the mock user
    access_token = user_service.create_access_token(user_id=mock_user.id)
    
    print(f"Generated Access Token: {access_token}")
    
    # Test GET endpoint
    response = client.get(f"{JOB_ENDPOINT}/{mock_job.id}", headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["title"] == "Test Job"
    assert response_data["description"] == "Test Description"
    assert response_data["location"] == "Test Location"
    assert response_data["salary"] == 2000.0
    assert response_data["job_type"] == "Full-time"
    assert response_data["company_name"] == "Test Company"