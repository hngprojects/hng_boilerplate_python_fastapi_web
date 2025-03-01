import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from api.v1.services.blog import BlogService
from api.v1.services.comment import CommentService
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Blog
from uuid_extensions import uuid7
from unittest.mock import MagicMock

client = TestClient(app)

@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="Test",
        last_name="User",
        is_active=True,
    )

@pytest.fixture
def test_blog(test_user):
    return Blog(
        id=str(uuid7()),
        author_id=test_user.id,
        title="Test Blog",
        content="Testing blog engagement."
    )

@pytest.fixture
def engagement_url(test_blog):
    return f"/api/v1/blogs/{test_blog.id}/engagement"

@pytest.fixture
def test_user_access_token(test_user):
    return user_service.create_access_token(user_id=test_user.id)

def test_get_blog_engagement(mock_db_session, test_blog, engagement_url, test_user_access_token, mocker):
    # Mock BlogService methods
    mock_blog_service = mocker.patch("api.v1.services.blog.BlogService", autospec=True)
    blog_service_instance = mock_blog_service.return_value
    blog_service_instance.fetch.return_value = test_blog
    blog_service_instance.num_of_likes.return_value = 5
    blog_service_instance.num_of_dislikes.return_value = 2
    
    # Mock CommentService method
    mock_comment_service = mocker.patch("api.v1.services.comment.CommentService", autospec=True)
    comment_service_instance = mock_comment_service.return_value
    comment_service_instance.get_comment_count.return_value = 3
    
    headers = {'Authorization': f'Bearer {test_user_access_token}'}
    response = client.get(engagement_url, headers=headers)
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json()['data']['likes'] == 5
    assert response.json()['data']['dislikes'] == 2
    assert response.json()['data']['comments'] == 3
