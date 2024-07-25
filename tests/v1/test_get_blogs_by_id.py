import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

from ...main import app
from api.v1.routes.blog import get_db
from api.v1.services.blog import BlogService

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


def create_mock_blog(id: str, author_id: str, title: str, content: str):
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)
    return {
        "id": id,
        "author_id": author_id,
        "title": title,
        "content": content,
        "image_url": "http://example.com/image.png",
        "tags": "test,blog",
        "is_deleted": False,
        "excerpt": "Test Excerpt",
        "created_at": timeinfo.isoformat(),
        "updated_at": timeinfo.isoformat()
    }


def test_fetch_blog_by_id(client, db_session_mock):
    id = "afa7addb-98a3-4603-8d3f-f36a31bcd1bd"
    author_id = "7ca7a05d-1431-4b2c-8968-6c510e85831b"
    mock_blog = create_mock_blog(id, author_id, "Test Title", "Test Content")

    db_session_mock.query().filter().first.return_value = mock_blog

    response = client.get(f"/api/v1/blogs/{id}")

    assert response.status_code == 200

    # Extract the JSON response data
    response_data = response.json()

    expected_response = {
        "success": True,
        "status_code": 200,
        "message": "Blog post retrieved successfully",
        "data": {
            "id": id,
            "author_id": author_id,
            "title": "Test Title",
            "content": "Test Content",
            "image_url": "http://example.com/image.png",
            "tags": 'test,blog',
            "is_deleted": False,
            "excerpt": "Test Excerpt",
            "created_at": mock_blog["created_at"],
            "updated_at": mock_blog["updated_at"]
        }
    }

    # Adjust the expected response to match the actual response structure
    assert response_data == expected_response


def test_fetch_blog_by_id_not_found(client, db_session_mock):
    id = "afa7addb-98a3-4603-8d3f-f36a31bcd1bd"

    db_session_mock.query().filter().first.return_value = None

    response = client.get(f"/api/v1/blogs/{id}")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "status_code": 404,
        "message": "Post not Found"
    }
