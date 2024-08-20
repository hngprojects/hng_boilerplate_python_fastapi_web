import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

from main import app
from api.v1.routes.blog import get_db


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


def test_fetch_blog_by_id_not_found(client, db_session_mock):
    id = "afa7addb-98a3-4603-8d3f-f36a31bcd1bd"

    db_session_mock.query().filter().first.return_value = None

    response = client.get(f"/api/v1/blogs/{id}")

    assert response.status_code == 404
