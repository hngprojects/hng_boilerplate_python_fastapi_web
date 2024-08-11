from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
import pytest
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.newsletter import NewsletterService
from api.v1.models.user import User
from api.v1.models.newsletter import Newsletter
from main import app


def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_newsletter():
    return Newsletter(
        id=str(uuid7()),
        title="Test newsletter title",
        content="Test newsletter content",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


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


def test_update_newsletter_success(client, db_session_mock):
    '''Test to successfully update a newsletter'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    app.dependency_overrides[NewsletterService.update] = lambda: mock_newsletter
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_newsletter_instance = mock_newsletter()

    with patch("api.v1.services.newsletter.NewsletterService.update", return_value=mock_newsletter_instance) as mock_update:
        response = client.patch(
            f'api/v1/newsletters/{mock_newsletter_instance.id}',
            headers={'Authorization': 'Bearer token'},
            json={
                "title": "Updated newsletter title",
                "content": "Updated newsletter content",
            }
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Successfully updated a newsletter"


def test_update_newsletter_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''
    mock_newsletter_instance = mock_newsletter()

    response = client.patch(
        f'api/v1/newsletters/{mock_newsletter_instance.id}',  # Use a placeholder ID for unauthorized access test
        json={
            "title": "Updated newsletter title",
            "content": "Updated newsletter content",
        }
    )

    assert response.status_code == 401
