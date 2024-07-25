# tests/test_jobs.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.db.database import Base, get_db
from api.utils.config import settings
from api.v1.models.job import Job

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

def test_update_job_success(client):
    response = client.put(
        "/api/v1/jobs/1",
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

def test_update_job_not_found(client):
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

def test_update_job_invalid_id(client):
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
    assert response.status_code == 422  # Unprocessable Entity
    # Further assertions for the specific validation error can be added

def test_update_job_missing_id(client):
    response = client.put(
        "/api/v1/jobs/",
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

def test_update_job_invalid_body(client):
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
    # Further assertions for the specific validation error can be added

def test_update_job_missing_token(client):
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
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
