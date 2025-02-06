import pytest
from main import app
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from api.db.database import get_db
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.v1.services.user import user_service
from api.v1.models import User, Blog, BlogDislike

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
def mock_blog_service():
    with patch("api.v1.services.blog.BlogService", autospec=True) as blog_service_mock:
        yield blog_service_mock


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
def test_blog_dislike(test_user, test_blog):
    return BlogDislike(
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
        f"/api/v1/blogs/{blog_id}/dislike",
        headers={"Authorization": f"Bearer {token}"}
    )


@patch("api.v1.services.blog.BlogService.create_blog_dislike")
def test_successful_dislike(
    mock_create_blog_dislike,
    mock_db_session, 
    test_user, 
    test_blog,
    test_blog_dislike,
    access_token_user
):
    # mock current-user AND blog-post
    mock_db_session.query().filter().first.side_effect = [test_user, test_blog]

    # mock existing-blog-dislike AND new-blog-dislike
    mock_db_session.query().filter_by().first.side_effect = None

    # mock created-blog-dislike
    mock_create_blog_dislike.return_value = test_blog_dislike

    # mock dislike-count
    mock_db_session.query().filter_by().count.return_value = 1

    resp = make_request(test_blog.id, access_token_user)
    resp_d = resp.json()
    assert resp.status_code == 200
    assert resp_d['success'] == True
    assert resp_d['message'] == "Dislike recorded successfully."

    dislike_data = resp_d['data']['object']
    assert dislike_data['id'] == test_blog_dislike.id
    assert dislike_data['blog_id'] == test_blog.id
    assert dislike_data['user_id'] == test_user.id
    assert dislike_data['ip_address'] == test_blog_dislike.ip_address
    assert datetime.fromisoformat(dislike_data['created_at']) == test_blog_dislike.created_at
    assert resp_d['data']['objects_count'] == 1


# Test for double dislike
def test_double_dislike(
    mock_db_session, 
    test_user, 
    test_blog, 
    test_blog_dislike,
    access_token_user,
):
    mock_user_service.get_current_user = test_user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_blog
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = test_blog_dislike

    ### TEST ATTEMPT FOR MULTIPLE DISLIKING... ###
    resp = make_request(test_blog.id, access_token_user)
    assert resp.status_code == 403
    assert resp.json()['message'] == "You have already disliked this blog post"

# Test for wrong blog id
def test_wrong_blog_id(
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