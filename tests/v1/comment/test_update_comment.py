import pytest
from fastapi.testclient import TestClient
from main import app  # Ensure you import your FastAPI app
from api.db.database import get_db
from unittest.mock import MagicMock
from api.v1.models.user import User
from api.v1.services.comment import comment_service
from api.v1.services.auth import get_current_user

client = TestClient(app)

# Override authentication dependency
app.dependency_overrides[get_current_user] = lambda: User(id="user-123")

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_current_user():
    return User(id="user-123")

@pytest.fixture
def mock_comment():
    return MagicMock(id="comment-123", user_id="user-123", content="Old content")

def test_update_comment_success(mock_db, mock_current_user, mock_comment, monkeypatch):
    monkeypatch.setattr(comment_service, "fetch", lambda db, id: mock_comment)
    monkeypatch.setattr(comment_service, "update_comments", lambda db, id, content: mock_comment)
    
    headers = {"Authorization": "Bearer valid_token"}
    response = client.patch(
        "/api/v1/comments/comment-123",
        json={"content": "Updated comment text"},
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Comment updated successfully"
    assert response.json()["data"]["content"] == "Updated comment text"

def test_update_comment_not_found(mock_db, mock_current_user, monkeypatch):
    monkeypatch.setattr(comment_service, "fetch", lambda db, id: None)
    
    headers = {"Authorization": "Bearer valid_token"}
    response = client.patch(
        "/api/v1/comments/invalid-id",
        json={"content": "Updated comment text"},
        headers=headers
    )
    
    assert response.status_code == 404
    assert response.json()["message"] == "Comment not found."

def test_update_comment_unauthorized(mock_db, mock_comment, monkeypatch):
    mock_comment.user_id = "another-user"
    monkeypatch.setattr(comment_service, "fetch", lambda db, id: mock_comment)
    
    headers = {"Authorization": "Bearer valid_token"}
    response = client.patch(
        "/api/v1/comments/comment-123",
        json={"content": "Updated comment text"},
        headers=headers
    )
    
    assert response.status_code == 403
    assert response.json()["message"] == "You do not have permission to edit this comment."
