from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.job import Job
from api.v1.services.user import user_service
from api.v1.models.job import JobApplication
from api.v1.services.job_application import job_application_service
from faker import Faker
from main import app


fake = Faker()

def mock_jpb():
    return Job(
        author_id=fake.uuid4(),
        title=fake.job(),
        description=fake.paragraph(),
        department=fake.random_element(["Engineering", "Marketing", "Sales"]),
        location=fake.city(),
        salary=fake.random_element(["$60,000 - $80,000", "$80,000 - $100,000"]),
        job_type=fake.random_element(["Full-time", "Contract", "Part-time"]),
        company_name=fake.company(),
    )

def mock_job_application():
    job = mock_jpb()
    
    return JobApplication(
        id=str(uuid7()),
        job_id=job.id,
        applicant_name = 'Test Applicant',
        applicant_email = 'user@example.com',
        cover_letter = 'Test cover letter',
        resume_link = 'https://www.example.com/portfolio',
        portfolio_link='https://www.example.com/portfolio',
        application_status='pending',
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


def test_create_job_application_success(client, db_session_mock):
    '''Test to successfully create a new job application'''

    # Mock the user service to return the current user
    app.dependency_overrides[job_application_service.create] = lambda: mock_job_application

    # Mock faq creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_job_app = mock_job_application()

    with patch("api.v1.services.job_application.job_application_service.create", return_value=mock_job_app) as mock_create:
        response = client.post(
            f'/api/v1/jobs/{mock_job_app.job_id}/applications',
            json={
                'applicant_name': 'Test Applicant',
                'applicant_email': 'user@example.com',
                'cover_letter': 'Test cover letter',
                'resume_link': 'https://www.example.com/portfolio',
                'portfolio_link': 'https://www.example.com/portfolio'
            }
        )

        assert response.status_code == 201


def test_create_job_application_already_applied(client, db_session_mock):
    '''Test to check if a user has already applied for the role'''

    # Mock the user service to return the current user
    app.dependency_overrides[job_application_service.create] = lambda: mock_job_application

    # Mock faq creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_job_app = mock_job_application()

    # Mock job application data
    mock_job_app = MagicMock(
        applicant_name="Test Applicant",
        applicant_email="user@example.com",
        cover_letter="Test cover letter",
        resume_link="https://www.example.com/resume",
        portfolio_link="https://www.example.com/portfolio",
        job_id=str(uuid7())
    )

    # Mock the database query to simulate that the user has already applied
    db_session_mock.query().filter().first.return_value = mock_job_app

    response =client.post(
        f'/api/v1/jobs/{mock_job_app.job_id}/applications',
        json={
            'applicant_name': 'Test Applicant',
            'applicant_email': 'user@example.com',
            'cover_letter': 'Test cover letter',
            'resume_link': 'https://www.example.com/portfolio',
            'portfolio_link': 'https://www.example.com/portfolio'
        }
    )

    assert response.status_code == 400


def test_create_job_application_missing_field(client, db_session_mock):
    '''Test for missing field when creating a new job application'''

    # Mock the user service to return the current user
    app.dependency_overrides[job_application_service.create] = lambda: mock_job_application

    # Mock faq creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_job_app = mock_job_application()

    with patch("api.v1.services.job_application.job_application_service.create", return_value=mock_job_app) as mock_create:
        response = client.post(
            f'/api/v1/jobs/{mock_job_app.job_id}/applications',
            json={
                'applicant_name': 'Test Applicant',
                'applicant_email': 'user@example.com',
                'resume_link': 'https://www.example.com/portfolio',
                'portfolio_link': 'https://www.example.com/portfolio'
            }
        )

        assert response.status_code == 422


def test_create_job_application_invalid_url(client, db_session_mock):
    '''Test to check for invalid url in job application creation'''

    # Mock the user service to return the current user
    app.dependency_overrides[job_application_service.create] = lambda: mock_job_application

    # Mock faq creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_job_app = mock_job_application()

    with patch("api.v1.services.job_application.job_application_service.create", return_value=mock_job_app) as mock_create:
        response = client.post(
            f'/api/v1/jobs/{mock_job_app.job_id}/applications',
            json={
                'applicant_name': 'Test Applicant',
                'applicant_email': 'user@example.com',
                'cover_letter': 'Test cover letter',
                'resume_link': 'http:/www.example.com/portfolio',
                'portfolio_link': 'https://www.example.com/portfolio'
            }
        )

        assert response.status_code == 422