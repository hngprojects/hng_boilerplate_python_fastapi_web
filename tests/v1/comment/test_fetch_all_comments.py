import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from main import app  # Adjust this import according to your project structure
from api.db.database import get_db

from api.v1.models.blog import Blog
from api.v1.models.comment import Comment
from api.v1.schemas.comment import CommentsSchema, CommentsResponse
from api.v1.services.comment import CommentService

# Create a test client for the FastAPI app
client = TestClient(app)

# Mocking the get_db dependency to return a session
@pytest.fixture
def db_session():
    session = MagicMock(spec=Session)
    yield session

@pytest.fixture
def comment_service_mock():
    return MagicMock()

# Overriding the dependency
@pytest.fixture(autouse=True)
def override_get_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

@pytest.fixture(autouse=True)
def override_comment_services(comment_service_mock):
    app.dependency_overrides[CommentService] = lambda: comment_service_mock

# Test the comments endpoint
def test_get_comments(db_session, comment_service_mock):
    user_id = 'test_user_id'
    blog_id = "test_blog_id"
    page = 1
    per_page = 20

    # Create mock blog and comments data
    blog = Blog(id=blog_id, author_id=user_id, content='some content', title='some title')
    comments = [
        Comment(user_id="user1", blog_id=blog_id, content="Comment 1", created_at="2023-07-28T12:00:00"),
        Comment(user_id="user2", blog_id=blog_id, content="Comment 2", created_at="2023-07-28T12:01:00")
    ]

    # Mocking the database query
    db_session.query.return_value.filter_by.return_value.one_or_none.return_value = blog
    db_session.query.return_value.filter_by.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = comments
    db_session.query.return_value.filter_by.return_value.count.return_value = len(comments)

    # Mocking the CommentServices.validate_params method
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

def test_get_comments_blog_not_found(db_session):
    """
    Test for non-existing blog
    """
    blog_id = "non_existent_blog_id"
    page = 1
    per_page = 20

    # Mocking the database query to return None for the blog
    db_session.query.return_value.filter_by.return_value.one_or_none.return_value = None

    response = client.get(f"/api/v1/blogs/{blog_id}/comments?page={page}&per_page={per_page}")

    assert response.status_code == 404
