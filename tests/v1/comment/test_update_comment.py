from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.blog import Blog
from api.v1.models.comment import Comment
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.services.comment import comment_service
from main import app


@pytest.fixture
def mock_get_current_user():
    """Mock get current user"""
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_comment(existing_blog_post, db_session_mock):
    """mock comments"""
    comment = Comment(
        id=str(uuid7()),
        blog_id=existing_blog_post.id,
        content="Updated Comment",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db_session_mock.query(Comment).\
        filter_by(id=comment.id).one_or_none.return_value = Comment
    return comment


@pytest.fixture
def existing_blog_post(mock_get_current_user):
    blog = Blog(
        id=f'{uuid7()}',
        title="Original Title",
        content="Original Content",
        author_id=mock_get_current_user.id
    )

    return blog


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


def test_update_comment_success(client, db_session_mock, mock_comment):
    '''Test to successfully create a new organization'''

    # Mock the user service to return the current user
    app.dependency_overrides[get_db] = lambda: db_session_mock
    app.dependency_overrides[
        user_service.get_current_user] = lambda: mock_get_current_user
    app.dependency_overrides[
        comment_service.update_comment] = lambda: mock_comment

    # Mock update comment
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    with patch(
        "api.v1.services.comment.comment_service.update_comment",
            return_value=mock_comment):
        response = client.patch(
            f'/api/v1/comments/edit/{mock_comment.id}',
            headers={'Authorization': 'Bearer token'},
            json={
                "content": "updated comment"
            }
        )

        assert response.status_code == 200


def test_update_comments_missing_field(client, db_session_mock):
    '''Test to successfully create a new organization'''

    app.dependency_overrides[
        user_service.get_current_user] = lambda: mock_get_current_user

    response = client.patch(
        '/api/v1/comments/edit/comment_id',
        headers={'Authorization': 'Bearer token'},
        json={
        }
    )

    assert response.status_code == 422


def test_update_comment_unauthorized(client, db_session_mock):
    '''Test to successfully create a new organization'''

    response = client.patch(
        '/api/v1/comments/edit/comment_id',
        json={
            "content": "updated content"
        }
    )

    assert response.status_code == 401
