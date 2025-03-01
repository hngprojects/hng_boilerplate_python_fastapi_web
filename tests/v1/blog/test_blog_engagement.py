import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from main import app
from api.v1.models.blog import Blog
from api.v1.routes.blog import get_db
from app.services.blog_service import BlogService
from app.services.comment_service import CommentService

# Initialize TestClient
client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

@pytest.fixture
def test_blog():
    blog_id = str(uuid7())
    author_id = str(uuid7())
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    created_at = datetime.now(tzinfo)
    updated_at = created_at
    
    return Blog(
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

# Test retrieving blogs when no blogs exist
def test_get_all_blogs_empty(mock_db_session):
    mock_db_session.query.return_value.count.return_value = 0
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
    
    response = client.get("/api/v1/blogs")
    assert response.status_code == 200
    assert response.json().get('data') == []

# Test retrieving blogs when data is present
def test_get_all_blogs_with_data(mock_db_session, test_blog):
    mock_db_session.query.return_value.count.return_value = 1
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [test_blog]
    
    response = client.get("/api/v1/blogs")
    assert response.status_code == 200
    assert len(response.json().get('data')) >= 1

@pytest.fixture
def mock_blog_service(mock_db_session):
    service = MagicMock(spec=BlogService)
    service.fetch.return_value = {"id": "123", "title": "Sample Blog"}
    service.num_of_likes.return_value = 100
    service.num_of_dislikes.return_value = 10
    return service

@pytest.fixture
def mock_comment_service():
    service = MagicMock(spec=CommentService)
    service.get_comment_count.return_value = 25
    return service

# Test retrieving engagement statistics
def test_get_blog_engagement_success(client, mock_db_session, mock_blog_service, mock_comment_service, monkeypatch):
    monkeypatch.setattr("app.services.blog_service.BlogService", lambda db: mock_blog_service)
    monkeypatch.setattr("app.services.comment_service.CommentService", lambda: mock_comment_service)
    
    response = client.get("/api/v1/123/engagement")
    assert response.status_code == 200
    assert response.json()["data"] == {"blog_id": "123", "likes": 100, "dislikes": 10, "comments": 25}

# Test when a blog post does not exist
def test_get_blog_engagement_not_found(client, mock_db_session, monkeypatch):
    mock_blog_service = MagicMock(spec=BlogService)
    mock_blog_service.fetch.return_value = None
    
    monkeypatch.setattr("app.services.blog_service.BlogService", lambda db: mock_blog_service)
    response = client.get("/api/v1/999/engagement")
    assert response.status_code == 404
    assert response.json()["detail"] == "Blog post not found"
