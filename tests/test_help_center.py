import datetime
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, MagicMock
from ..main import app


# Initialize TestClient
client = TestClient(app)

# Mock JWT token
VALID_JWT_TOKEN = "valid-jwt-token"
INVALID_JWT_TOKEN = "invalid-jwt-token"

# Mock headers
headers = {
    "Authorization": f"Bearer {VALID_JWT_TOKEN}",
    "Content-Type": "application/json"
}

# Mock database as a global dictionary
db = {}

@pytest.fixture
def setup_db():
    db["valid-id"] = {
        "id": "valid-id",
        "title": "Original Title",
        "content": "Original content",
        "author": "Original Author",
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
    }
    yield
    db.clear()

@patch('test.database.get_db', return_value=db)
def test_update_topic_success(mock_get_db, setup_db):
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "author": "Updated Author"
    }

    with patch('main.update_topic_in_db') as mock_update_topic:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": "valid-id",
                "title": "Updated Title",
                "content": "Updated content",
                "author": "Updated Author",
                "created_at": str(datetime.datetime.now()),
                "updated_at": str(datetime.datetime.now()),
            },
            "status_code": 200
        }
        mock_update_topic.return_value = mock_response
        
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

def test_patch_topic_unauthorized():
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "author": "Updated Author"
    }

    response = client.patch(
        "/api/v1/help-center/topics/valid-id",
        headers={"Content-Type": "application/json"},  # No Authorization header
        json=update_data
    )

    assert response.status_code == 401
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Access denied. No token provided or token is invalid"
    assert data["status_code"] == 401

@patch('main.get_current_user', return_value={"role": "user"})
def test_update_topic_forbidden(mock_get_current_user, setup_db):
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "author": "Updated Author"
    }

    with patch('main.update_topic_in_db') as mock_update_topic:
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "success": False,
            "message": "Access denied",
            "status_code": 403
        }
        mock_update_topic.return_value = mock_response
        
        response = client.patch(
            "/api/v1/help-center/topics/valid-id",
            headers=headers,
            json=update_data
        )

    assert response.status_code == 403
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Access denied"
    assert data["status_code"] == 403

@patch('main.get_db', return_value=db)
def test_update_topic_not_found(mock_get_db):
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "author": "Updated Author"
    }

    with patch('main.update_topic_in_db') as mock_update_topic:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "success": False,
            "message": "Article not found",
            "status_code": 404
        }
        mock_update_topic.return_value = mock_response
        
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

@patch('main.get_db', return_value=db)
def test_update_topic_invalid_input(mock_get_db, setup_db):
    update_data = {
        "title": "",
        "content": "Updated content",
        "author": "Updated Author"
    }

    with patch('main.update_topic_in_db') as mock_update_topic:
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "success": False,
            "message": "Invalid input data",
            "status_code": 422
        }
        mock_update_topic.return_value = mock_response
        
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
