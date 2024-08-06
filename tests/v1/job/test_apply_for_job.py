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


# def mock_get_current_user():
#     return User(
#         id=str(uuid7()),
#         email="testuser@gmail.com",
#         password=user_service.hash_password("Testpassword@123"),
#         first_name='Test',
#         last_name='User',
#         is_active=True,
#         is_super_admin=False,
#         created_at=datetime.now(timezone.utc),
#         updated_at=datetime.now(timezone.utc)
#     )


# def mock_get_current_admin():
#     return User(
#         id=str(uuid7()),
#         email="admin@gmail.com",
#         password=user_service.hash_password("Testadmin@123"),
#         first_name='Admin',
#         last_name='User',
#         is_active=True,
#         is_super_admin=True,
#         created_at=datetime.now(timezone.utc),
#         updated_at=datetime.now(timezone.utc)
#     )

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