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


@patch("api.v1.services.newsletter.NewsletterService.unsubscribe")
def test_newsletter_subscribe_missing_fields(mock_unsubscribe, db_session_mock, client):
    """Tests the POST /api/v1/newsletter-subscription endpoint for missing required fields."""

    mock_unsubscribe.return_value = None

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    response = client.post("/api/v1/newsletter-subscription", json={})
    assert response.status_code == 422
