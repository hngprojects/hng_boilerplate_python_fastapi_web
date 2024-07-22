from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.db.database import get_db
from api.v1.models.job import Job
from api.v1.models.user import User
from api.v1.schemas.job import JobSchema

from ...main import app

# from uuid import uuid7

client = TestClient(app)


# Mock the database dependency
@pytest.fixture
def db_session_mock(mocker):
    db_session = mocker.MagicMock()
    yield db_session


# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(mocker, db_session_mock):
    mocker.patch("app.routes.job.get_db", return_value=db_session_mock)


def test_get_job_by_id_success(db_session_mock):
    # Arrange
    user_1 = User(
        username="user1",
        email="user1@example.com",
        password="password1",
        first_name="User",
        last_name="One",
        is_active=True,
    )
    job = Job(
        user_id=user_1.id,
        title="Software Engineer",
        description="Develop and maintain software applications.",
        location="New York, NY",
        salary=120000.00,
        job_type="Full-time",
        company_name="Tech Innovations Inc.",
    )
    db_session_mock.query(Job).get.return_value = job

    # Act
    response = client.get(f"/api/v1/jobs/{job.id}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": job.id,
        "user_id": user_1.id,
        "title": "Software Engineer",
        "description": "Develop and maintain software applications.",
        "location": "New York, NY",
        "salary": 120000.00,
        "job_type": "Full-time",
        "company_name": "Tech Innovations Inc.",
    }


def test_get_job_by_id_not_found(db_session_mock):
    # Arrange
    db_session_mock.query(Job).get.return_value = None

    # Act
    response = client.get(f"/api/v1/jobs/")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


if __name__ == "__main__":
    pytest.main()
