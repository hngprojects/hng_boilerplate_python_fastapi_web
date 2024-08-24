import pytest
from main import app
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from api.db.database import get_db
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.v1.services.blog import BlogService
from api.v1.services.user import user_service
from api.v1.models import User, Blog, BlogLike

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock


@pytest.fixture
def mock_user_service():
    with patch("api.v1.services.user.user_service", autospec=True) as user_service_mock:
        yield user_service_mock


@pytest.fixture
def mock_blog_service(mock_db_session):
    with patch("api.v1.services.blog.BlogService", autospec=True) as blog_service_mock:
        yield blog_service_mock(mock_db_session)


# Test User
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )

@pytest.fixture()
def test_blog(test_user):
    return Blog(
        id=str(uuid7()),
        author_id=test_user.id,
        title="Blog Post 1",
        content="This is blog post number 1"
    )

@pytest.fixture()
def test_blog_like(test_user, test_blog):
    return BlogLike(
            id=str(uuid7()),
            user_id=test_user.id,
            blog_id=test_blog.id,
            ip_address="192.168.1.0",
            created_at=datetime.now(tz=timezone.utc)
        )

@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)

def make_request(blog_id, token):
    return client.post(
        f"/api/v1/blogs/{blog_id}/like",
        headers={"Authorization": f"Bearer {token}"}
    )

# Test for successful like
@patch("api.v1.services.blog.BlogService.create_blog_like")
def test_successful_like(
    mock_create_blog_like,
    mock_db_session, 
    test_user, 
    test_blog,
    test_blog_like,
    access_token_user
):
    # mock current-user AND blog-post
    mock_db_session.query().filter().first.side_effect = [test_user, test_blog]

    # mock existing-blog-like
    mock_db_session.query().filter_by().first.return_value = None

    # mock created-blog-like
    mock_create_blog_like.return_value = test_blog_like

    # mock like-count
    mock_db_session.query().filter_by().count.return_value = 1

    resp = make_request(test_blog.id, access_token_user)
    resp_d = resp.json()
    print(resp_d)
    assert resp.status_code == 200
    assert resp_d['success'] == True
    assert resp_d['message'] == "Like recorded successfully."

    like_data = resp_d['data']['object']
    assert like_data['id'] == test_blog_like.id
    assert like_data['blog_id'] == test_blog.id
    assert like_data['user_id'] == test_user.id
    assert like_data['ip_address'] == test_blog_like.ip_address
    assert datetime.fromisoformat(like_data['created_at']) == test_blog_like.created_at
    assert resp_d['data']['objects_count'] == 1


# Test for double like
def test_double_like(
    mock_db_session, 
    test_user, 
    test_blog, 
    test_blog_like,
    access_token_user,
):
    mock_user_service.get_current_user = test_user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_blog
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = test_blog_like

    ### TEST ATTEMPT FOR MULTIPLE DISLIKING... ###
    resp = make_request(test_blog.id, access_token_user)
    assert resp.status_code == 403
    assert resp.json()['message'] == "You have already liked this blog post"

# Test for wrong blog id
def test_wrong_blog_id(
    # mock_fetch_blog,
    mock_db_session, 
    test_user,
    access_token_user,
):
    mock_user_service.get_current_user = test_user
    mock_db_session.query().filter().first.return_value = None

    ### TEST REQUEST WITH WRONG blog_id ###
    ### using random uuid instead of blog1.id  ###
    resp = make_request(str(uuid7()), access_token_user)
    assert resp.status_code == 404
    assert resp.json()['message'] == "Post not found"


# Test for unauthenticated user
def test_wrong_auth_token(
    mock_db_session,
    test_blog
):
    mock_user_service.get_current_user = None

    ### TEST ATTEMPT WITH INVALID AUTH... ###
    resp = make_request(test_blog.id, None)
    assert resp.status_code == 401
    assert resp.json()['message'] == 'Could not validate credentials'
