import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.blog import Blog
from api.v1.models.comment import Comment
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from faker import Faker

fake = Faker()
client = TestClient(app)


@pytest.fixture
def mock_db_session(mocker):
    """Mock the database session."""
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock


@pytest.fixture
def test_user():
    """Create a test user."""
    return User(
        id=str(uuid7()),
        email=fake.email(),
        password=fake.password(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=True,
    )


@pytest.fixture
def test_blog(test_user):
    """Create a test blog."""
    return Blog(
        id=str(uuid7()),
        author_id=test_user.id,
        title=fake.sentence(),
        content=fake.paragraph(nb_sentences=3),
    )


@pytest.fixture
def test_comment(test_user, test_blog):
    """Create a test comment."""
    return Comment(
        id=str(uuid7()),
        user_id=test_user.id,
        blog_id=test_blog.id,
        content=fake.paragraph(nb_sentences=2),
    )


@pytest.fixture
def access_token_user(test_user):
    """Generate an access token for the test user."""
    return user_service.create_access_token(user_id=test_user.id)


def test_create_reply_success(
        mock_db_session, test_user, test_comment, access_token_user
    ):
    """Test successful reply creation."""
    def mock_get(model, ident):
        if model == Comment and ident == test_comment.id:
            return test_comment
        return None

    mock_db_session.get.side_effect = mock_get

    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    headers = {'Authorization': f'Bearer {access_token_user}'}
    data = {"content": "This is a reply to the comment."}

    response = client.post(
        f"/api/v1/comments/{test_comment.id}/reply", json=data, headers=headers
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Reply to comment created successfully"
    assert response.json()["data"]["content"] == data["content"]


def test_create_reply_unprocessable_entity(
        mock_db_session, test_user, test_comment, access_token_user
    ):
    """Test reply creation with empty content (422)."""
    headers = {'Authorization': f'Bearer {access_token_user}'}
    data = {"content": ""}  # Empty reply

    response = client.post(
        f"/api/v1/comments/{test_comment.id}/reply", json=data, headers=headers
    )

    assert response.status_code == 422
    assert response.json()["message"] == "Invalid input"


def test_create_reply_invalid_comment_id(
        mock_db_session, test_user, access_token_user
    ):
    """Test reply creation with a non-existent comment ID (404)."""
    def mock_get(model, ident):
        return None  # Simulating a missing comment

    mock_db_session.get.side_effect = mock_get

    headers = {'Authorization': f'Bearer {access_token_user}'}
    data = {"content": "This is a reply to a non-existent comment."}

    response = client.post(
        "/api/v1/comments/invalid-comment-id/reply", json=data, headers=headers
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Comment does not exist"


def test_create_reply_unauthorized(mock_db_session, test_comment):
    """Test unauthorized reply creation (401)."""
    data = {"content": "This is a reply, but user is not authenticated."}

    response = client.post(f"/api/v1/comments/{test_comment.id}/reply", json=data)

    assert response.status_code == 401
    assert response.json()["message"] == "Not authenticated"
