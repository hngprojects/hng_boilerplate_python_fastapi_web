import pytest
from unittest.mock import patch, MagicMock
from api.v1.models.user import User
from api.v1.services.user import user_service
from main import app
from uuid_extensions import uuid7
from api.db.database import get_db
from api.v1.models.community import CommunityQuestion
from fastapi import status
from datetime import datetime, timezone, timedelta


CREATE_QUESTION_ENDPOINT = '/api/v1/community/questions/create'
GET_ALL_QUESTIONS_ENDPOINT = '/api/v1/community/questions'
GET_QUESTION_BY_ID_ENDPOINT = '/api/v1/community/questions/{question_id}'
GET_QUESTIONS_BY_USER_ENDPOINT = '/api/v1/community/questions/user/{user_id}'
UPDATE_QUESTION_ENDPOINT = '/api/v1/community/questions/{question_id}'
MARK_RESOLVED_ENDPOINT = '/api/v1/community/questions/{question_id}/resolve'
DELETE_QUESTION_ENDPOINT = '/api/v1/community/questions/{question_id}'

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


def create_mock_user(mock_user_service, mock_db_session, is_superadmin=True):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=is_superadmin,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

@pytest.fixture
def mock_question_service():
    """Fixture to create a mock activity log service."""
    with patch("api.v1.services.community.community_question_service",autospec=True) as mock_service:
        yield mock_service

def create_mock_question(mock_db_session, question_id="1", title="Test Question", message="Test message", user_id="101", is_resolved=False):
    """Create a mock community question in the mock database session."""
    mock_question = CommunityQuestion(
        id=question_id,
        title=title,
        message=message,
        user_id=user_id,
        is_resolved=is_resolved,
        timestamp="2023-01-01T00:00:00"
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_question
    return mock_question
