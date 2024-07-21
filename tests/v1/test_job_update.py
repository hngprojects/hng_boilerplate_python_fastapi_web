import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from api.v1.models.job import Job
from api.v1.models.user import User

client = TestClient(app)

# Mock data
mock_job = Job(
    id="1",
    title="Existing Job",
    description="Existing Description",
    location="Existing Location",
    salary=50000.0,
    job_type="Full-Time",
    company_name="Existing Company",
    user_id="user_id"
)

mock_user = User(
    id="user_id",
    is_admin=False
)

mock_admin_user = User(
    id="admin_id",
    is_admin=True
)


@pytest.fixture
def override_get_db():
    with patch("api.v1.route.job.get_db") as mock_get_db:
        mock_session = MagicMock()
        mock_get_db.return_value = mock_session
        yield mock_session


@pytest.fixture
def override_get_current_user():
    with patch("api.v1.route.job.get_current_user") as mock_get_current_user:
        mock_get_current_user.return_value = mock_user
        yield mock_get_current_user


@pytest.fixture
def override_get_current_admin_user():
    with patch("api.v1.route.job.get_current_user") as mock_get_current_user:
        mock_get_current_user.return_value = mock_admin_user
        yield mock_get_current_user


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


def test_update_job_post_success(test_client, override_get_db, override_get_current_user):
    mock_session = override_get_db
    mock_session.query(Job).filter(Job.id == "1").first.return_value = mock_job

    response = test_client.patch(
        "/api/v1/jobs/1",
        json={"title": "Updated Job Title"},
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Job details updated successfully"


def test_update_job_post_not_found(test_client, override_get_db, override_get_current_user):
    mock_session = override_get_db
    mock_session.query(Job).filter(Job.id == "999").first.return_value = None

    response = test_client.patch(
        "/api/v1/jobs/999",
        json={"title": "Updated Job Title"},
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Job post not found"


def test_update_job_post_unauthorized(test_client, override_get_db):
    mock_session = override_get_db
    mock_session.query(Job).filter(Job.id == "1").first.return_value = mock_job

    response = test_client.patch(
        "/api/v1/jobs/1",
        json={"title": "Updated Job Title"},
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this job post"


def test_update_job_post_success_admin(test_client, override_get_db, override_get_current_admin_user):
    mock_session = override_get_db
    mock_session.query(Job).filter(Job.id == "1").first.return_value = mock_job

    response = test_client.patch(
        "/api/v1/jobs/1",
        json={"title": "Updated Job Title"},
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Job details updated successfully"


def test_update_job_post_invalid_body(test_client, override_get_db, override_get_current_user):
    mock_session = override_get_db
    mock_session.query(Job).filter(Job.id == "1").first.return_value = mock_job

    response = test_client.patch(
        "/api/v1/jobs/1",
        json={"title": 12345},  # Invalid data type
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 422
