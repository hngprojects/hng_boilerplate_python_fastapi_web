import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from main import app
from api.v1.models.blog import Blog
from api.v1.models.comment import Comment  # Import your Comment model
from api.v1.routes.blog import get_db

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

def test_get_comments_for_blog_empty(client, db_session_mock):
    blog_id = uuid7()  # Example blog_id

    # Mock the return value for the comments query
    db_session_mock.query().filter().all.return_value = []

    # Call the endpoint
    response = client.get(f"/api/v1/blogs/{blog_id}/comments")

    # Assert the response
    assert response.status_code == 200
    assert response.json() == []

def test_get_comments_for_blog_with_data(client, db_session_mock):
    blog_id = uuid7()
    author_id = uuid7()
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)
    created_at = timeinfo
    updated_at = timeinfo

    # Create a mock blog post
    blog = Blog(
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

    # Create a mock comment
    comment = Comment(
        id=uuid7(),
        blog_id=blog_id,
        author_id=author_id,
        content="Test Comment",
        created_at=created_at,
        updated_at=updated_at
    )

    # Mock the return value for the comments query
    db_session_mock.query().filter().all.return_value = [comment]

    # Call the endpoint
    response = client.get(f"/api/v1/blogs/{blog_id}/comments")

    # Assert the response
    assert response.status_code == 200
    assert response.json() == [{
        "id": str(comment.id),
        "blog_id": str(comment.blog_id),
        "author_id": str(comment.author_id),
        "content": "Test Comment",
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat()
    }]
