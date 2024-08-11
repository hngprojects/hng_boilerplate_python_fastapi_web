from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.faq import FAQ
from api.v1.services.faq import faq_service
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


def mock_faq():
    return FAQ(
        id=str(uuid7()),
        question="TTest qustion?",
        answer="TAnswer",
        category="Category",
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


def test_update_faq_success(client, db_session_mock):
    '''Test to successfully update a new faq'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    app.dependency_overrides[faq_service.update] = lambda: mock_faq

    # Mock faq creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_freq_asked_questions = mock_faq()

    with patch("api.v1.services.faq.faq_service.update", return_value=mock_freq_asked_questions) as mock_update:
        response = client.patch(
            f'/api/v1/faqs/{mock_freq_asked_questions.id}',
            headers={'Authorization': 'Bearer token'},
            json={
                "question": "Question?",
                "answer": "Answer",
                "category": "Updated category",
            }
        )

        assert response.status_code == 200


def test_update_faq_missing_field(client, db_session_mock):
    '''Test for missing field when creating a new faq'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    app.dependency_overrides[faq_service.update] = lambda: mock_faq

    # Mock faq creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_freq_asked_questions = mock_faq()

    with patch("api.v1.services.faq.faq_service.update", return_value=mock_freq_asked_questions) as mock_update:
        response = client.patch(
            f'/api/v1/faqs/{mock_freq_asked_questions.id}',
            headers={'Authorization': 'Bearer token'},
            json={
                "question": "Question?"
            }
        )

        assert response.status_code == 422


def test_update_faq_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''

    mock_freq_asked_questions = mock_faq()

    response = client.patch(
        f'/api/v1/faqs/{mock_freq_asked_questions.id}',
        headers={'Authorization': 'Bearer token'},
        json={
            "question": "Question?",
            "answer": "Answer",
            "category": "Category",
        }
    )

    assert response.status_code == 401


def test_faq_not_found(client, db_session_mock):
    """Test when the FAQ ID does not exist."""

    # Mock the user service to return the current super admin user
    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_admin
    app.dependency_overrides[faq_service.fetch] = lambda: mock_faq

    # Simulate a non-existent organisation
    nonexistent_id = str(uuid7())

    # Mock the organisation service to raise an exception for a non-existent FAQ
    with patch("api.v1.services.faq.faq_service.fetch", side_effect=HTTPException(status_code=404, detail="FAQ not found")):
        response = client.patch(
            f'/api/v1/faqs/{nonexistent_id}',
            headers={'Authorization': 'Bearer valid_token'},
            json={
                "question": "Question?",
                "answer": "Answer",
                "category": "Category",
            }
        )

        # Assert that the response status code is 404 Not Found
        assert response.status_code == 404
        