import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def admin_token():
    # Replace this with actual logic to obtain a valid admin token
    return "your_admin_token"

def test_create_job(admin_token):
    response = client.post(
        "/api/v1/jobs/create",
        json={
            "title": "Software Engineer",
            "description": "Develop software",
            "company": "TechCorp",
            "location": "Remote",
            "salary": 70000,
            "is_active": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Software Engineer"
    assert data["description"] == "Develop software"
    assert data["company"] == "TechCorp"
    assert data["location"] == "Remote"
    assert data["salary"] == 70000
    assert data["is_active"] == True

def test_create_job_unauthorized():
    response = client.post(
        "/api/v1/jobs/create",
        json={
            "title": "Software Engineer",
            "description": "Develop software",
            "company": "TechCorp",
            "location": "Remote",
            "salary": 70000,
            "is_active": True
        }
    )
    
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized"}
