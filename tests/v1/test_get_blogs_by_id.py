import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from pydantic import HttpUrl
from fastapi import HTTPException
from uuid_extensions import uuid7
from ...main import app
from api.v1.models.blog import Blog as BlogModel
from api.v1.routes.blog import get_db
from api.v1.services.blog import BlogService

from api.v1.schemas.blog import Blog as BlogSchema

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

# Helper function to create a mock blog


def create_mock_blog(id: int, author_id: str, title: str, content: str):
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)
    return BlogModel(
        id=id,
        author_id=author_id,
        title=title,
        content=content,
        image_url=["http://example.com/image.png"],
        tags=["test", "blog"],
        is_deleted=False,
        excerpt="Test Excerpt",
        likes=None,
        dislikes=None,
        likes_audit=None,
        dislikes_audit=None,
        created_at=timeinfo,
        updated_at=timeinfo
    )


def test_fetch_blog_by_id(client, db_session_mock):
    id = uuid7()
    author_id = str(uuid7())
    mock_blog = create_mock_blog(id, author_id, "Test Title", "Test Content")

    # Mock the fetch method of BlogService to return the mock_blog
    with patch.object(BlogService, 'fetch', return_value=mock_blog):
        response = client.get(f"/api/v1/blogs/{id}")

        print("Actual Response:", response.json())
        expected_response = {
            "id": str(id),
            "author_id": author_id,
            "title": "Test Title",
            "content": "Test Content",
            "image_url": ["http://example.com/image.png"],
            "tags": ["test", "blog"],
            "is_deleted": False,
            "excerpt": "Test Excerpt",
            "likes": None,
            "dislikes": None,
            "likes_audit": None,
            "dislikes_audit": None,
            "created_at": mock_blog.created_at.isoformat(),
            "updated_at": mock_blog.updated_at.isoformat()
        }
        print("Expected Response:", expected_response)

        assert response.status_code == 200
        assert response.json() == expected_response


def test_fetch_blog_by_id_not_found(client, db_session_mock):
    blog_service = BlogService()
    id = uuid7()

    with patch.object(BlogService, 'fetch', side_effect=HTTPException(status_code=404, detail="Blog post not found")):
        response = client.get(f"/api/v1/blogs/{id}")

        print("Response for Not Found:", response.json())

        assert response.status_code == 404
        assert response.json() == {
            "success": False, "status_code": 404, "message": "Blog post not found"}
