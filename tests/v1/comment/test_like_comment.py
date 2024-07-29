import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.models.blog import Blog
from api.v1.models.comment import Comment
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone
from faker import Faker

fake = Faker() 

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""

    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service

@pytest.fixture
def mock_comment_service():
    """Fixture to create a mock comment service."""
    
    with patch("api.v1.services.comment.comment_service", autospec=True) as mock_service:
        yield mock_service



def create_mock_user(mock_user_service, mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = User(
        email=fake.email(),
        username=fake.user_name(),
        password=user_service.hash_password(fake.password()),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

def create_mock_user1(mock_user_service, mock_db_session):
    mock_user_1= User(
        email=fake.email(),
        username=fake.user_name(),
        password=user_service.hash_password(fake.password()),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user_1
    return mock_user_1

def create_mock_blog(mock_user_service, mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_blog = Blog(
        author_id=mock_user.id,
        title=fake.sentence(),
        content=fake.paragraphs(nb=3, ext_word_list=None),
        image_url=fake.image_url(),
        excerpt=fake.paragraph(),
        tags=fake.words(nb=3)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_blog
    return mock_blog

def create_mock_comment(mock_user_service, mock_db_session):
    mock_user1 = create_mock_user1(mock_user_service, mock_db_session)
    mock_blog = create_mock_blog(mock_user_service, mock_db_session)
    mock_comment = Comment(
        user_id=mock_user1.id,
        blog_id=mock_blog.id,
        content=fake.paragraph(),
    )
    return mock_comment



@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_fetch_all_plans(mock_user_service, mock_db_session):
    """Test for user deactivation errors."""
    mock_comment_like = create_mock_comment(mock_user_service, mock_db_session)
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    response = client.post(f'/api/v1/comments/{str(uuid7())}/like'
                               , headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == status.HTTP_200_OK
    
