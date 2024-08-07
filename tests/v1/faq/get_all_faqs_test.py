from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.faq import FAQ
from api.v1.services.faq import faq_service
from main import app


@pytest.fixture
def mock_db_session():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_get_all_faqs(mock_db_session, client):
    """Test to verify the pagination response for FAQs."""
    # Mock data
    mock_faq_data = [
        FAQ(id=1, question="Question 1", answer="Answer 1"),
        FAQ(id=2, question="Question 2", answer="Answer 2"),
        FAQ(id=3, question="Question 3", answer="Answer 3"),
    ]

    app.dependency_overrides[faq_service.fetch_all] = mock_faq_data

    # Perform the GET request
    response = client.get('/api/v1/faqs')

    # Verify the response
    assert response.status_code == 200
