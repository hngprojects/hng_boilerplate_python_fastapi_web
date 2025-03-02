from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from freezegun import freeze_time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.v1.models.blog import Blog, BlogStatus
from api.v1.models.user import User
from api.v1.routes.blog import get_db
from api.v1.services.user import user_service
from api.v1.schemas.blog import BlogResponse
from main import app


# Mock database dependency
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


def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="user@gmail.com",
        password=user_service.hash_password("Testuser@123"),
        first_name="User",
        last_name="User",
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_create_scheduled_blog_success(client, db_session_mock):
    # Setup test data
    scheduled_time = datetime.now() + timedelta(minutes=1)

    blog_data = {
        "title": "Scheduled Test Blog",
        "content": "Test Content",
        "image_url": "http://example.com/image.png",
        "tags": ["test", "scheduled"],
        "excerpt": "Test Excerpt",
        "scheduled_at": scheduled_time.isoformat()
    }

    # Create a mock blog instance from blog_data
    mock_blog = Blog(**blog_data)

    app.dependency_overrides[user_service.get_current_user] = mock_get_current_user

    # Mock the database operations
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_blog

    # Make the request
    response = client.post(
        "/api/v1/blogs/",
        json=blog_data,
        headers={"Authorization": "Bearer token"},
    )

    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Blog post scheduled successfully!"
    assert response_data["data"]["title"] == blog_data["title"]
    assert response_data["data"]["status"] == BlogStatus.PENDING.value
    assert "scheduled_at" in response_data["data"]



def test_create_scheduled_blog_past_date(client, db_session_mock):
    # Test scheduling a blog in the past
    past_time = datetime.now() - timedelta(days=1)

    app.dependency_overrides[user_service.get_current_user] = (
        mock_get_current_user
    )

    # Mock the database add and commit operations
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    blog_data = {
        "title": "Past Scheduled Blog",
        "content": "Test Content",
        "image_url": "http://example.com/image.png",
        "tags": ["test"],
        "excerpt": "Test Excerpt",
        "scheduled_at": past_time.isoformat(),
    }

    response = client.post(
        "/api/v1/blogs/",
        json=blog_data,
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 400
    assert "Scheduled time must be in the future." in response.json()["message"]


def test_create_scheduled_blog_unauthenticated(client, db_session_mock):
    # Remove super admin override to test unauthorized access
    app.dependency_overrides[user_service.get_current_user] = lambda: None
    scheduled_time = datetime.now() + timedelta(minutes=1)

    blog_data = {
        "title": "Past Scheduled Blog",
        "content": "Test Content",
        "image_url": "http://example.com/image.png",
        "tags": ["test"],
        "excerpt": "Test Excerpt",
        "scheduled_at": scheduled_time.isoformat(),
    }

    response = client.post("/api/v1/blogs/", json=blog_data)

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["message"]


def test_scheduled_blog_is_published_after_scheduled_time(client, db_session_mock):
    # Setup initial time
    current_time = datetime.now(timezone.utc)
    scheduled_time = current_time + timedelta(minutes=1)
    
    # Create a mock blog
    mock_blog = Blog(
        id=str(uuid7()),
        title="Scheduled Test Blog",
        content="Test Content",
        image_url="http://example.com/image.png",
        tags=["test", "scheduled"],
        excerpt="Test Excerpt",
        scheduled_at=scheduled_time,
        status=BlogStatus.PENDING,
        author_id=str(uuid7()),
        is_deleted=False
    )

    # Mock the database query to return our blog
    def mock_query_filter(*args):
        mock = MagicMock()
        mock.all.return_value = [mock_blog]
        return mock

    db_session_mock.query.return_value.filter.side_effect = mock_query_filter
    
    # Verify blog status is pending
    assert mock_blog.status == BlogStatus.PENDING  

    # Create scheduler with mocked db
    from api.v1.services.blog_scheduler import BlogScheduler
    scheduler = BlogScheduler(app)
    scheduler.db = db_session_mock  # Use our mocked db

    # Move time forward and run the scheduler
    with freeze_time(scheduled_time + timedelta(minutes=1)):
        scheduler.publish_schedule_blog()
        # Verify commit was called
        db_session_mock.commit.assert_called_once()
        # Verify blog status was updated
        assert mock_blog.status == BlogStatus.PUBLISHED


        
def test_retrieve_scheduled_blogs(client, db_session_mock):
    # Setup test data
    scheduled_time = datetime.now() + timedelta(minutes=1)
    blog_data = {
        "title": "Scheduled Test Blog",
        "content": "Test Content",
        "image_url": "http://example.com/image.png",
        "tags": ["test", "scheduled"],
        "excerpt": "Test Excerpt",
        "scheduled_at": scheduled_time.isoformat(),
    }
    # Mock the database query to return our blog
    def mock_query_filter(*args):
        mock = MagicMock()
        mock.all.return_value = [mock_blog]
        return mock
   
    
    app.dependency_overrides[user_service.get_current_user] = (
        mock_get_current_user
    )

    # Create a mock blog instance from blog_data
    mock_blog = Blog(**blog_data)

    # Mock the database operations
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None
    db_session_mock.query.return_value.filter.side_effect = mock_query_filter

    # Make the request
    response = client.get(
        "/api/v1/blogs/scheduled",
        headers={"Authorization": "Bearer token"},
    )   

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Scheduled blogs retrieved successfully"
    assert response_data["data"][0]["title"] == mock_blog.title
