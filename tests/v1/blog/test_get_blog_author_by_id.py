import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

from main import app
from api.v1.routes.blog import get_db


@pytest.fixture
def db_session_mock():
    """Fixture to create a mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def client(db_session_mock):
    """Fixture to override FastAPI dependency injection for testing."""
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides = {}


def create_mock_blog(blog_id: uuid.UUID, author_id: uuid.UUID, title: str):
    """Helper function to create a mock blog object with UUIDs."""
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)
    return {
        "id": str(blog_id),
        "author_id": str(author_id),
        "title": title,
        "content": "Sample content",
        "image_url": "http://example.com/image.png",
        "tags": "test,blog",
        "is_deleted": False,
        "excerpt": "Test Excerpt",
        "created_at": timeinfo.isoformat(),
        "updated_at": timeinfo.isoformat()
    }


def test_get_blogs_by_author(client, db_session_mock):
    """Test retrieving blogs by an author using UUIDs."""
    author_id = uuid.uuid4()
    mock_blogs = [
        create_mock_blog(uuid.uuid4(), author_id, "Blog 1"),
        create_mock_blog(uuid.uuid4(), author_id, "Blog 2"),
    ]

    db_session_mock.query().filter().order_by().offset().limit().all.return_value = mock_blogs

    response = client.get(f"/api/v1/blogs/author/{author_id}")

    assert response.status_code == 200
    assert len(response.json()["data"]["items"]) == 2  # Fixed assertion
    assert response.json()["data"]["items"][0]["title"] == "Blog 1"


def test_get_blogs_by_author_empty(client, db_session_mock):
    """Test retrieving blogs by an author when no blogs exist."""
    author_id = uuid.uuid4()

    db_session_mock.query().filter().order_by().offset().limit().all.return_value = []

    response = client.get(f"/api/v1/blogs/author/{author_id}")

    assert response.status_code == 200
    assert response.json()["data"]["items"] == []  # Fixed assertion


