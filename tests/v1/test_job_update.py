import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.job import Job
from api.db.database import get_db

def create_test_user(db: Session, is_admin: bool = False):
    user = User(email="test@example.com", password="testpassword", is_admin=is_admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_test_job(db: Session, user_id: str):
    job = Job(
        title="Test Job",
        description="Test Description",
        location="Test Location",
        salary="1000",
        job_type="Full-time",
        company_name="Test Company",
        user_id=user_id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@pytest.fixture(scope="function")
def test_data():
    db = next(get_db())
    user = create_test_user(db)
    admin_user = create_test_user(db, is_admin=True)
    job = create_test_job(db, user.id)
    return {"user": user, "admin_user": admin_user, "job": job}

def test_update_job_post(test_client: TestClient, test_data):
    job_id = test_data["job"].id
    user_token = "fake-jwt-token-for-test-user"  # Use your method to create a token
    update_data = {
        "title": "Updated Test Job",
        "description": "Updated Test Description",
        "location": "Updated Test Location",
        "salary": "2000",
        "job_type": "Part-time",
        "company_name": "Updated Test Company"
    }

    response = test_client.patch(
        f"/api/v1/jobs/{job_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["data"]["title"] == "Updated Test Job"
    assert response_data["data"]["description"] == "Updated Test Description"

def test_update_job_post_not_found(test_client: TestClient):
    user_token = "fake-jwt-token-for-test-user"  # Use your method to create a token
    update_data = {
        "title": "Updated Test Job"
    }

    response = test_client.patch(
        f"/api/v1/jobs/non-existent-id",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Job post not found"

def test_update_job_post_unauthorized(test_client: TestClient, test_data):
    job_id = test_data["job"].id
    unauthorized_user_token = "fake-jwt-token-for-unauthorized-user"  # Use your method to create a token
    update_data = {
        "title": "Updated Test Job"
    }

    response = test_client.patch(
        f"/api/v1/jobs/{job_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {unauthorized_user_token}"}
    )

    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Not authorized to update this job post"
