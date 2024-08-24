import pytest
from main import app
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from api.db.database import get_db
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.v1.models import User, BlogDislike
from api.v1.services.user import user_service

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


# Another User
@pytest.fixture
def another_user():
    return User(
        id=str(uuid7()),
        email="anotheruser@gmail.com",
        password="hashedpassword",
        first_name="another",
        last_name="user",
        is_active=True,
    )

@pytest.fixture
def test_blog_dislike(test_user):
    return BlogDislike(
            id=str(uuid7()),
            user_id=test_user.id,
            blog_id=str(uuid7()),
            ip_address="192.168.1.0",
            created_at=datetime.now(tz=timezone.utc)
        )

@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)

@pytest.fixture
def access_token_another(another_user):
    return user_service.create_access_token(user_id=another_user.id)


def make_request(blog_dislike_id, token):
    return client.delete(
        f"/api/v1/blogs/dislikes/{blog_dislike_id}",
        headers={"Authorization": f"Bearer {token}"}
    )


# test for successful delete
@patch("api.v1.services.blog.BlogDislikeService.fetch")
def test_successful_delete_blog_dislike(
    mock_fetch_blog_dislike,
    mock_db_session, 
    test_user,
    test_blog_dislike,
    access_token_user
):
    # mock current-user AND blog-like
    mock_db_session.query().filter().first.return_value = test_user
    mock_fetch_blog_dislike.return_value = test_blog_dislike

    resp = make_request(test_blog_dislike.id, access_token_user)
    assert resp.status_code == 204


# Test for wrong blog like id
def test_wrong_blog_dislike_id(
    mock_db_session, 
    test_user,
    access_token_user,
):
    mock_db_session.query().filter().first.return_value = test_user
    mock_db_session.get.return_value = None

    ### TEST REQUEST WITH WRONG blog_dislike_id ###
    resp = make_request(str(uuid7()), access_token_user)
    assert resp.status_code == 404
    assert resp.json()['message'] == "BlogDislike does not exist"


# Test for unauthenticated user
def test_wrong_auth_token(
    test_blog_dislike
):
    mock_user_service.get_current_user = None

    ### TEST ATTEMPT WITH INVALID AUTH ###
    resp = make_request(test_blog_dislike.id, None)
    assert resp.status_code == 401
    assert resp.json()['message'] == 'Could not validate credentials'


# Test for wrong owner request
def test_wrong_owner_request(
    mock_db_session,
    test_blog_dislike,
    another_user,
    access_token_another
):
    mock_user_service.get_current_user = another_user
    mock_db_session.get.return_value = test_blog_dislike

    ### TEST ATTEMPT BY NON OWNER ###
    resp = make_request(test_blog_dislike.id, access_token_another)
    assert resp.status_code == 401
    assert resp.json()['message'] == 'Insufficient permission'