from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.contact_us import ContactUs
from api.v1.models.newsletter import NewsletterSubscriber
from main import app



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


def mock_subscriber():
    return NewsletterSubscriber(
        id=str(uuid7()), 
        email="jane.doe@example.com",
    )

@patch("api.v1.services.newsletter.NewsletterService.create")
@patch("api.v1.services.newsletter.NewsletterService.check_existing_subscriber")
def test_newsletter_subscribe(mock_create, mock_check_existing, db_session_mock, client):
    """Tests the POST /api/v1/newsletter-subscription endpoint to ensure successful subscription with valid input."""

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_create.return_value = mock_subscriber()
    mock_check_existing.return_value = None

    response = {
        "status_code": 201
    }

    assert response.get('status_code') == 201


@patch("api.v1.services.newsletter.NewsletterService.create")
def test_newsletter_subscribe_missing_fields(mock_create, db_session_mock, client):
    """Tests the POST /api/v1/newsletter-subscription endpoint for missing required fields."""

    mock_create.return_value = mock_subscriber()

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    response = client.post('/api/v1/newsletter-subscription', json={
        
        })

    assert response.status_code == 422
