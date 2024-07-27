import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from api.v1.services.job_service import JobService
from api.v1.models.job import Job
from api.v1.routes.job import Job
from unittest.mock import MagicMock

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_update_job_success(client, mocker):
    mock_job = MagicMock(spec=Job)
    mock_job.id = "1"
    mock_job.user_id = "user1"
    mock_job.title = "Original Title"

    mocker.patch.object(JobService, "get_job_by_id", return_value=mock_job)
    mocker.patch.object(JobService, "update_job", return_value=mock_job)

    response = client.put(
        "/api/v1/jobs",
        json={
            "title": "Updated Title",
            "description": "Updated Description",
            "location": "Updated Location",
            "salary": "Updated Salary",
            "job_type": "Updated Job Type",
            "company_name": "Updated Company Name"
        },
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Job details updated successfully"

def test_update_job_not_found(client, mocker):
    mocker.patch.object(JobService, "get_job_by_id", return_value=None)

    response = client.put(
        "/api/v1/jobs/9999",
        json={
            "title": "Title",
            "description": "Description",
            "location": "Location",
            "salary": "Salary",
            "job_type": "Job Type",
            "company_name": "Company Name"
        },
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

def test_update_job_invalid_id(client, mocker):
    response = client.put(
        "/api/v1/jobs/invalid_id",
        json={
            "title": "Title",
            "description": "Description",
            "location": "Location",
            "salary": "Salary",
            "job_type": "Job Type",
            "company_name": "Company Name"
        },
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 422  

def test_update_job_invalid_body(client, mocker):
    mock_job = MagicMock(spec=Job)
    mocker.patch.object(JobService, "get_job_by_id", return_value=mock_job)

    response = client.put(
        "/api/v1/jobs/1",
        json={
            "title": 123,  # Invalid type
            "description": "Description",
            "location": "Location",
            "salary": "Salary",
            "job_type": "Job Type",
            "company_name": "Company Name"
        },
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 422  # Unprocessable Entity

def test_update_job_missing_token(client, mocker):
    mock_job = MagicMock(spec=Job)
    mocker.patch.object(JobService, "get_job_by_id", return_value=mock_job)

    response = client.put(
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
    assert response.status_code == 401  # Unauthorized
    assert response.json()["detail"] == "Not authenticated"
