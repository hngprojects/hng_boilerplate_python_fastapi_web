from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.v1.models.blog import Blog
from api.v1.routes.blog import get_db
from main import app
from app.services.blog_service import BlogService
from app.services.comment_service import CommentService


# Mock database dependency
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

def test_get_all_blogs_empty(client, db_session_mock):
    """Test retrieving blogs when no blogs exist."""
    # Mock data
    mock_blog_data = []
    
    mock_query = MagicMock()
    mock_query.count.return_value = 0
    db_session_mock.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_blog_data

    db_session_mock.query.return_value = mock_query

    # Call the endpoint
    response = client.get("/api/v1/blogs")

    # Assert the response
    assert response.status_code == 200

def test_get_all_blogs_with_data(client, db_session_mock):
    """Test retrieving blogs when data is present."""
    blog_id = str(uuid7())
    author_id = str(uuid7())
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)
    created_at = timeinfo
    updated_at = timeinfo

    # Mock data
    mock_blog_data = [
        Blog(
            id=blog_id,
            author_id=author_id,
            title="Test Blog",
            content="Test Content",
            image_url="http://example.com/image.png",
            tags=["test", "blog"],
            is_deleted=False,
            excerpt="Test Excerpt",
            created_at=created_at,
            updated_at=updated_at
        )
    ]
    
    mock_query = MagicMock()
    mock_query.count.return_value = 1
    db_session_mock.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_blog_data

    db_session_mock.query.return_value = mock_query

    # Call the endpoint
    response = client.get("/api/v1/blogs")

    # Assert the response
    assert response.status_code == 200
    assert len(response.json().get('data')) >= 1


# ----------------- ENGAGEMENT TEST CASES -----------------

@pytest.fixture
def mock_blog_service(db_session_mock):
    """Fixture to provide a mocked BlogService."""
    service = MagicMock(spec=BlogService)
    service.fetch.return_value = {"id": "123", "title": "Sample Blog"}
    service.num_of_likes.return_value = 100
    service.num_of_dislikes.return_value = 10
    return service

@pytest.fixture
def mock_comment_service():
    """Fixture to provide a mocked CommentService."""
    service = MagicMock(spec=CommentService)
    service.get_comment_count.return_value = 25
    return service

def test_get_blog_engagement_success(
    client, db_session_mock, mock_blog_service, mock_comment_service, monkeypatch
):
    """Test retrieving engagement statistics for an existing blog post."""
    
    # Mock dependencies
    monkeypatch.setattr("app.routes.blog.BlogService", lambda db: mock_blog_service)
    monkeypatch.setattr("app.routes.blog.CommentService", lambda: mock_comment_service)

    response = client.get("/api/v1/123/engagement")

    assert response.status_code == 200
    data = response.json()
    
    assert data["status_code"] == 200
    assert data["message"] == "Engagement statistics retrieved successfully"
    assert data["data"] == {
        "blog_id": "123",
        "likes": 100,
        "dislikes": 10,
        "comments": 25,
    }

def test_get_blog_engagement_not_found(client, db_session_mock, monkeypatch):
    """Test when a blog post does not exist, should return 404."""
    
    mock_blog_service = MagicMock(spec=BlogService)
    mock_blog_service.fetch.return_value = None  # Simulate blog not found

    monkeypatch.setattr("app.routes.blog.BlogService", lambda db: mock_blog_service)

    response = client.get("/api/v1/999/engagement")

    assert response.status_code == 404
    assert response.json()["detail"] == "Blog post not found"
