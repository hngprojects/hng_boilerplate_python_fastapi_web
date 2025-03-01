import pytest
from fastapi.testclient import TestClient
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogRequest
from api.v1.services.user import user_service
# Initialize TestClient
client = TestClient(app)

# Fixture: Mock BlogService
@pytest.fixture
def mock_blog_service():
    service = MagicMock(spec=BlogService)
    service.fetch.return_value = {"id": "123", "title": "Sample Blog"}
    service.num_of_likes.return_value = 100
    service.num_of_dislikes.return_value = 10
    return service

# Fixture: Mock CommentService
@pytest.fixture
def mock_comment_service():
    service = MagicMock(spec=CommentService)
    service.get_comment_count.return_value = 25
    return service

# Test retrieving engagement statistics
def test_get_blog_engagement_success(mock_blog_service, mock_comment_service, monkeypatch):
    monkeypatch.setattr("app.services.blog_service.BlogService", lambda db: mock_blog_service)
    monkeypatch.setattr("app.services.comment_service.CommentService", lambda: mock_comment_service)
    
    response = client.get("/api/v1/123/engagement")
    assert response.status_code == 200
    assert response.json()["data"] == {
        "blog_id": "123",
        "likes": 100,
        "dislikes": 10,
        "comments": 25
    }

# Test when a blog post does not exist
def test_get_blog_engagement_not_found(monkeypatch):
    mock_blog_service = MagicMock(spec=BlogService)
    mock_blog_service.fetch.return_value = None  # Simulate blog not found
    
    monkeypatch.setattr("app.services.blog_service.BlogService", lambda db: mock_blog_service)
    
    response = client.get("/api/v1/999/engagement")
    assert response.status_code == 404
    assert response.json()["detail"] == "Blog post not found"
