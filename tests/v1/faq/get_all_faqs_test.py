from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
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


def test_get_all_faqs_grouped_by_category(mock_db_session, client):
    """Test to verify the response for FAQs grouped by category."""

    mock_faq_data_grouped = {
        "General": [
            {"question": "What is FastAPI?",
                "answer": "FastAPI is a modern web framework for Python."},
            {"question": "What is SQLAlchemy?",
                "answer": "SQLAlchemy is a SQL toolkit and ORM for Python."}
        ],
        "Billing": [
            {"question": "How do I update my billing information?",
                "answer": "You can update your billing information in the account settings."}
        ]
    }

    with patch.object(faq_service, 'fetch_all_grouped_by_category', return_value=mock_faq_data_grouped):

        response = client.get('/api/v1/faqs')

    assert response.status_code == 200
