from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.v1.models.job import Job
from api.v1.services.jobs import job_service
from main import app


def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_job():
    return Job(
        id=str(uuid7()),
        title="Test job title",
        description="Test job description",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_update_job_success(client, db_session_mock):
    '''Test to successfully update a job'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    app.dependency_overrides[job_service.update] = lambda: mock_job

    # Mock job update
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_job_instance = mock_job()

    with patch("api.v1.services.jobs.job_service.update", return_value=mock_job_instance) as mock_update:
        response = client.patch(
            f'api/v1/jobs/{mock_job_instance.id}',
            headers={'Authorization': 'Bearer token'},
            json={
                "title": "Updated job title",
                "description": "Updated job description",
            }
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Successfully updated a job listing"


def test_update_job_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''

    mock_job_instance = mock_job()

    response = client.patch(
        f'api/v1/jobs/{mock_job_instance.id}',
        json={
            "title": "Updated job title",
            "description": "Updated job description",
        }
    )

    assert response.status_code == 401
