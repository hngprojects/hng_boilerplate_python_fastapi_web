import datetime
from api.db.database import get_db
import pytest
from fastapi.testclient import TestClient
from ..main import app


db = get_db()
client = TestClient(app)

# Mock JWT token
VALID_JWT_TOKEN = "valid-jwt-token"
INVALID_JWT_TOKEN = "invalid-jwt-token"

# Mock headers
headers = {
    "Authorization": f"Bearer {VALID_JWT_TOKEN}",
    "Content-Type": "application/json"
}

@pytest.fixture
def setup_db():
    db["valid-id"] = {
        "id": "valid-id",
        "title": "Original Title",
        "content": "Original content",
        "author": "Original Author",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    yield
    db.clear()

def test_update_topic_success(setup_db):
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "author": "Updated Author"
    }
    response = client.patch(
        "/api/v1/help-center/topics/valid-id",
        headers=headers,
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["title"] == "Updated Title"
    assert data["data"]["content"] == "Updated content"
    assert data["data"]["author"] == "Updated Author"
    assert data["status_code"] == 200

def test_update_topic_unauthorized():
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "author": "Updated Author"
    }
    response = client.patch(
        "/api/v1/help-center/topics/valid-id",
        headers={"Authorization": f"Bearer {INVALID_JWT_TOKEN}"},
        json=update_data
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Access denied. No token provided or token is invalid"
    assert data["status_code"] == 401

def test_update_topic_forbidden(setup_db):
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "author": "Updated Author"
    }
    # Temporarily change the get_current_user function to simulate a non-admin user
    original_get_current_user = main.get_current_user
    main.get_current_user = lambda token: "user"
    
    response = client.patch(
        "/api/v1/help-center/topics/valid-id",
        headers=headers,
        json=update_data
    )
    
    # Restore the original get_current_user function
    main.get_current_user = original_get_current_user
    
    assert response.status_code == 403
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Access denied"
    assert data["status_code"] == 403

def test_update_topic_not_found():
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "author": "Updated Author"
    }
    response = client.patch(
        "/api/v1/help-center/topics/invalid-id",
        headers=headers,
        json=update_data
    )
    assert response.status_code == 404
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Article not found"
    assert data["status_code"] == 404

def test_update_topic_invalid_input(setup_db):
    update_data = {
        "title": "",
        "content": "Updated content",
        "author": "Updated Author"
    }
    response = client.patch(
        "/api/v1/help-center/topics/valid-id",
        headers=headers,
        json=update_data
    )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Invalid input data"
    assert data["status_code"] == 422
