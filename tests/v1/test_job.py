from uuid import uuid4

import pytest
from decouple import config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.db.database import Base, get_db
from api.utils.auth import hash_password
from api.v1.models.job import Job  # Assuming Job is the model name
from api.v1.models.user import User
from main import app

# Database configuration
SQLALCHEMY_DATABASE_URL = config("DB_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()


def create_user(test_db):
    # Add user to database
    user = User(
        username="testuser",
        email="testuser@gmail.com",
        password=hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_admin=False,
    )

    test_db.add(user)
    test_db.commit()

    test_db.refresh(user)
    return user.id


def create_job(test_db, user_id):
    job = Job(
        user_id=user_id,
        title="Test Job Title",
        description="Test job description",
        location="Test location",
        salary="1000",
        job_type="Test Job Type",
        company_name="Test Company Name",
    )
    test_db.add(job)
    test_db.commit()
    test_db.refresh(job)
    return job


def test_get_job_by_id_success(test_db):
    # Create a job in the test database
    user_id = create_user(test_db)
    job = create_job(test_db, user_id)

    # Make a request to get the job by ID
    response = client.get(f"/api/v1/jobs/{job.id}")

    # Assert the response
    assert response.status_code == 200
    assert response.json() == {
        "statusCode": 200,
        "message": "Job retrieval successful",
        "data": {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "salary": job.salary,
            "job_type ": job.job_type,
            "company_name ": job.company_name,
            "created_at ": job.created_at,
            "updated_at ": job.updated_at,
        },
    }


def test_get_job_by_id_not_found(test_db):
    # Make a request to get a job that does not exist
    response = client.get("/api/v1/jobs/999")

    # Assert the response
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


if __name__ == "__main__":
    pytest.main()
