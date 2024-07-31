from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.v1.models.blog import Blog
from api.v1.routes.blog import get_db

from main import app


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

