import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Blog, Comment, Engagement
from uuid_extensions import uuid7

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
def test_engagement(test_user, test_blog):
    return Engagement(
        id=str(uuid7()),
        user_id=test_user.id,
        blog_id=test_blog.id,
        likes=5,
        shares=2,
        comments=3
    )

@pytest.fixture
def engagement_url(test_blog):
    return f"/api/v1/blogs/{test_blog.id}/engagement"

@pytest.fixture
def test_user_access_token(test_user):
    return user_service.create_access_token(user_id=test_user.id)

def test_get_blog_engagement(mock_db_session, test_blog, test_engagement, engagement_url, test_user_access_token):
    def mock_get(model, ident):
        if model == Blog and ident == test_blog.id:
            return test_blog
        elif model == Engagement and ident == test_engagement.id:
            return test_engagement
        return None

    mock_db_session.get.side_effect = mock_get
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_engagement

    headers = {'Authorization': f'Bearer {test_user_access_token}'}
    response = client.get(engagement_url, headers=headers)

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json()['data']['likes'] == test_engagement.likes
    assert response.json()['data']['shares'] == test_engagement.shares
    assert response.json()['data']['comments'] == test_engagement.comments
