import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Job, JobApplication
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from unittest.mock import MagicMock

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

# Test User 
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )


# Test Super admin 
@pytest.fixture
def test_admin():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
        is_superadmin=True
    )

# Test Job 
@pytest.fixture
def test_job(test_user):
    return Job(
        id=str(uuid7()), 
        author_id=test_user.id, 
        description="Test job one", 
        title="Engineer"
        )

# Test Job Application
@pytest.fixture
def test_application(test_job, test_user):
    JobApplication(
        id=str(uuid7()), 
        job_id=test_job.id, 
        applicant_name=test_user.first_name, 
        applicant_email=test_user.id,
        resume_link="lakjfoaldflaf"
        )

# Access token for test user
@pytest.fixture
def user_access_token(test_user):
    return user_service.create_access_token(user_id=test_user.id)

# Access token for test super admin
@pytest.fixture
def admin_access_token(test_admin):
    return user_service.create_access_token(user_id=test_admin.id)

# Test fetching applications with authenticated super admin 
def test_fetching_with_superadmin(
    mock_db_session, 
    test_job,
    test_application,
    admin_access_token,
):
    # Mock the GET method for Job ID
    def mock_get(model, ident):
        if model == Job and ident == test_job.id:
            return test_job
        return None

    mock_db_session.get.side_effect = mock_get

    # Mock the query to return test user
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = test_application

    # Test get all applications
    headers = {'Authorization': f'Bearer {admin_access_token}'}
    response = client.get(f"/api/v1/jobs/{test_job.id}/applications", headers=headers)
    
    # Debugging statement
    if response.status_code != 200:
        print(response.json())  # Print error message for more details

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json()['message'] == "Successfully fetched job applications"

# Test fetching applications with authenticated non super admin 
def test_fetching_with_non_superadmin(
    mock_db_session, 
    test_user, 
    test_job,
    test_application,
    user_access_token,
):
    # Mock the GET method for Job ID
    def mock_get(model, ident):
        if model == Job and ident == test_job.id:
            return test_job
        return None

    mock_db_session.get.side_effect = mock_get

    # Mock the query to return test user
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = test_application

    # Test get all applications
    headers = {'Authorization': f'Bearer {test_user}'}
    response = client.get(f"/api/v1/jobs/{test_job.id}/applications", headers=headers)
    
    assert response.status_code == 401, f"Expected status code 200, got {response.status_code}"

