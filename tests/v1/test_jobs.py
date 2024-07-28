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


@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_get_current_user(mocker):
    user = MagicMock(spec=User)
    user.id = 'user1'
    user.is_super_admin = False
    mocker.patch('api.utils.dependencies.get_current_user', return_value=user)

@pytest.fixture(autouse=True)
def mock_jwt_decode(mocker):
    mocker.patch('jwt.decode', return_value={"user_id": "user1"})

@pytest.fixture
def valid_token():
    return "Bearer valid_token"

def create_mock_job():
    mock_job = MagicMock(spec=Job)
    mock_job.id = "1"
    mock_job.user_id = "user1"
    mock_job.title = "Original Title"
    mock_job.description = "Description"
    mock_job.location = "Location"
    mock_job.salary = "Salary"
    mock_job.job_type = "Job Type"
    mock_job.company_name = "Company Name"
    mock_job.created_at = "2021-01-01T00:00:00"
    mock_job.updated_at = "2021-01-01T00:00:00"
    return mock_job

def test_update_job_success(client: TestClient, mocker: MockerFixture, valid_token: str):
    mock_job = create_mock_job()

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
    data = response.json()["data"]
    assert data["title"] == "Original Title"
    assert data["description"] == "Description"
    assert data["location"] == "Location"
    assert data["salary"] == "Salary"
    assert data["job_type"] == "Job Type"
    assert data["company_name"] == "Company Name"
    assert data["created_at"] == "2021-01-01T00:00:00"
    assert data["updated_at"] == "2021-01-01T00:00:00"

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
    assert response.json().get("detail") == "Job post not found"

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
    mock_job = create_mock_job()
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
    mock_job = create_mock_job()
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