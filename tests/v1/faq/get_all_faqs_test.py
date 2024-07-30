from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.faq import FAQ
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
    
    mock_query = MagicMock()
    mock_query.count.return_value = 3
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_faq_data

    mock_db_session.query.return_value = mock_query

    # Perform the GET request
    response = client.get('/api/v1/faqs', params={'limit': 2, 'skip': 0})

    # Verify the response
    assert response.status_code == 200


def test_get_all_faqs_with_skip(mock_db_session, client):
    """Test to verify the pagination response for FAQs."""

    # Mock data
    mock_faq_data = [
        FAQ(id=1, question="Question 1", answer="Answer 1"),
        FAQ(id=2, question="Question 2", answer="Answer 2"),
        FAQ(id=3, question="Question 3", answer="Answer 3"),
    ]
    
    mock_query = MagicMock()
    mock_query.count.return_value = 3
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_faq_data

    mock_db_session.query.return_value = mock_query


    # Perform the GET request
    response = client.get('/api/v1/faqs', params={'limit': 2, 'skip': 2})

    # Verify the response
    assert response.status_code == 200
