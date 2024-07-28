import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from api.v1.services.job_service import JobService
from api.v1.models.job import Job
from api.db.database import get_db
from api.v1.models.user import User
from pytest_mock import MockerFixture

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

# Mock jwt.decode
@pytest.fixture
def mock_jwt_decode(mocker):
    return mocker.patch('jwt.decode', return_value={"user_id": "user_id"})    
    

@pytest.fixture
def mock_get_current_user(mocker):
    user = User(id='user_id', is_super_admin=False)
    mock = mocker.patch('api.utils.dependencies.get_current_user', return_value=user)
    return mock

# Client for sending test requests
@pytest.fixture(scope="module")
def client():
    return TestClient(app)

# Override the get_current_user dependency with a mock user
@pytest.fixture(autouse=True)
def mock_get_current_user(mocker):
    user = User(id='user1', is_super_admin=False)
    mocker.patch('api.utils.dependencies.get_current_user', return_value=user)

# A valid token, in a real scenario this should be a properly signed JWT
@pytest.fixture
def valid_token():
    return "Bearer valid_token"

# Tests

def test_update_job_success(client: TestClient, mocker: MockerFixture, valid_token: str):
    mock_job = MagicMock(spec=Job)
    mock_job.id = "1"
    mock_job.user_id = "user1"
    mock_job.title = "Original Title"

    mocker.patch.object(JobService, "get_job_by_id", return_value=mock_job)
    mocker.patch.object(JobService, "update_job", return_value=mock_job)

    response = client.patch(
        "/api/v1/jobs/1",
        json={
            "title": "Updated Title",
            "description": "Updated Description",
            "location": "Updated Location",
            "salary": "Updated Salary",
            "job_type": "Updated Job Type",
            "company_name": "Updated Company Name"
        },
        headers={"Authorization": valid_token}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Job details updated successfully"

def test_update_job_not_found(client: TestClient, mocker: MockerFixture, valid_token: str):
    mocker.patch.object(JobService, "get_job_by_id", return_value=None)

    response = client.patch(
        "/api/v1/jobs/9999",
        json={
            "title": "Title",
            "description": "Description",
            "location": "Location",
            "salary": "Salary",
            "job_type": "Job Type",
            "company_name": "Company Name"
        },
        headers={"Authorization": valid_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Job post not found"

def test_update_job_invalid_id(client: TestClient, valid_token: str):
    response = client.patch(
        "/api/v1/jobs/invalid_id",
        json={
            "title": "Title",
            "description": "Description",
            "location": "Location",
            "salary": "Salary",
            "job_type": "Job Type",
            "company_name": "Company Name"
        },
        headers={"Authorization": valid_token}
    )
    assert response.status_code == 422

def test_update_job_invalid_body(client: TestClient, mocker: MockerFixture, valid_token: str):
    mock_job = MagicMock(spec=Job)
    mocker.patch.object(JobService, "get_job_by_id", return_value=mock_job)

    response = client.patch(
        "/api/v1/jobs/1",
        json={
            "title": 123,  # Invalid type
            "description": "Description",
            "location": "Location",
            "salary": "Salary",
            "job_type": "Job Type",
            "company_name": "Company Name"
        },
        headers={"Authorization": valid_token}
    )
    assert response.status_code == 422

def test_update_job_missing_token(client: TestClient, mocker: MockerFixture):
    mock_job = MagicMock(spec=Job)
    mocker.patch.object(JobService, "get_job_by_id", return_value=mock_job)

    response = client.patch(
        "/api/v1/jobs/1",
        json={
            "title": "Title",
            "description": "Description",
            "location": "Location",
            "salary": "Salary",
            "job_type": "Job Type",
            "company_name": "Company Name"
        }
    )
    assert response.status_code == 401