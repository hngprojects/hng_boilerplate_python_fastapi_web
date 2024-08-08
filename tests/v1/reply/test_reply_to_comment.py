from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.blog import Blog
from api.v1.models.comment import Comment
from api.v1.models.reply import Reply
from main import app


def mock_get_current_user():
    return User(
        id="test_user_id",
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_blog():
    return Blog(
        id="test_blog_id",
        author_id="test_user_id",
        title="Test Blog",
        content="Test Content",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_comment():
    return Comment(
        id="test_comment_id",
        user_id="test_user_id",
        blog_id="test_blog_id",
        content="Test Comment",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


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


def test_reply_to_a_comment_success(client, db_session_mock):
    '''Test to successfully reply to a comment'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user

    # Mock reply creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_reply = Reply(
        id=str(uuid7()),
        user_id="test_user_id",
        comment_id="test_comment_id",
        content="This is a test reply",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    with patch("api.v1.services.reply.reply_service.create", return_value=mock_reply) as mock_create:
        response = client.post(
            '/api/v1/comments/test_comment_id/reply',
            headers={'Authorization': 'Bearer token'},
            json={
                "content": "This is a test reply"
            }
        )

        assert response.status_code == 201
        assert response.json()["message"] == "Reply added successfully"
        assert response.json()["data"]["content"] == "This is a test reply"
        assert response.json()["data"]["comment_id"] == "test_comment_id"
        assert response.json()["data"]["user_id"] == "test_user_id"


def test_reply_to_a_comment_missing_field(client, db_session_mock):
    '''Test for missing field when replying to a comment'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user

    response = client.post(
        '/api/v1/comments/test_comment_id/reply',
        headers={'Authorization': 'Bearer token'},
        json={}
    )

    assert response.status_code == 422


def test_reply_to_a_comment_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''

    response = client.post(
        '/api/v1/comments/test_comment_id/reply',
        json={
            "content": "This is a test reply"
        }
    )

    assert response.status_code == 401
