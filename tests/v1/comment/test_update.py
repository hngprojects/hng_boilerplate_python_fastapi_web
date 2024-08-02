import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from main import app
from api.db.database import get_db

from api.v1.models.blog import Blog
from api.v1.models.comment import Comment
from api.v1.schemas.comment import CommentsSchema, CommentsResponse
from api.v1.services.comment import CommentService

client = TestClient(app)

@pytest.fixture
def db_session():
    session = MagicMock(spec=Session)
    yield session

@pytest.fixture
def comment_service_mock():
    return MagicMock()

@pytest.fixture(autouse=True)
def override_get_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

@pytest.fixture(autouse=True)
def override_comment_services(comment_service_mock):
    app.dependency_overrides[CommentService] = lambda: comment_service_mock

def test_update_comments(db_session, comment_service_mock):
    user_id = 'test_user_id'
    blog_id = "test_blog_id"
    page = 1
    per_page = 20

    blog = Blog(id=blog_id, author_id=user_id, content='some content', title='some title')
    comments = [
        Comment(user_id="user1", blog_id=blog_id, content="Comment 1", created_at="2023-07-28T12:00:00"),
        Comment(user_id="user2", blog_id=blog_id, content="Comment 2", created_at="2023-07-28T12:01:00")
    ]

    db_session.query.return_value.filter_by.return_value.one_or_none.return_value = blog
    db_session.query.return_value.filter_by.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = comments
    db_session.query.return_value.filter_by.return_value.count.return_value = len(comments)

    comment_service_mock.validate_params.return_value = CommentsResponse(
        page=page,
        per_page=per_page,
        total=len(comments),
        data=[CommentsSchema.model_validate(comment) for comment in comments]
    )

    response = client.get(f"/api/v1/blogs/{blog_id}/comments?page={page}&per_page={per_page}")

    assert response.status_code == 200
    assert response.json() == {
        "page": page,
        "per_page": per_page,
        "total": len(comments),
        "data": [
            {
                "user_id": "user1",
                "blog_id": blog_id,
                "content": "Comment 1",
                "likes": [],
                "dislikes": [],
                "created_at": "2023-07-28T12:00:00"
            },
            {
                "user_id": "user2",
                "blog_id": blog_id,
                "content": "Comment 2",
                "likes": [],
                "dislikes": [],
                "created_at": "2023-07-28T12:01:00"
            }
        ]
    }

def test_update_comments_not_found(db_session):
    """
    Test for non-existing blog
    """
    blog_id = "non_existent_blog_id"
    page = 1
    per_page = 20

    db_session.query.return_value.filter_by.return_value.one_or_none.return_value = None

    response = client.get(f"/api/v1/blogs/{blog_id}/comments?page={page}&per_page={per_page}")

    assert response.status_code == 404
    assert response.json() == {'message': 'Blog not found', 'status_code': 404, 'success': False}
