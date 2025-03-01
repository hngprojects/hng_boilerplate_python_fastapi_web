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


def test_filter_faq_by_category(mock_db_session, client):
    """Test to verify the response for filtering FAQs by category."""

    mock_faq_data_grouped = {
        "General": [
            {"question": "What is FastAPI?",
                "answer": "FastAPI is a modern web framework for Python."},
            {"question": "What is SQLAlchemy?",
                "answer": "SQLAlchemy is a SQL toolkit and ORM for Python."}
        ]
    }

    with patch.object(faq_service, 'fetch_all_grouped_by_category', return_value=mock_faq_data_grouped):
        response = client.get('/api/v1/faqs/?category=General')
        response_data = response.json()

    assert response.status_code == 200
    assert response_data["status_code"] == 200
    assert response_data["message"] == "FAQs retrieved successfully"
    assert "General" in response_data["data"]
    assert len(response_data["data"]["General"]) == 2
    assert response_data["data"]["General"][0]["question"] == "What is FastAPI?"
    assert response_data["data"]["General"][1]["question"] == "What is SQLAlchemy?"


def test_filter_faq_category_not_found(mock_db_session, client):
    """Test when the requested category does not exist."""

    mock_faq_data_grouped = {}

    with patch.object(faq_service, 'fetch_all_grouped_by_category', return_value=mock_faq_data_grouped):
        response = client.get('/api/v1/faqs/?category=UnknownCategory')
        response_data = response.json()

    assert response.status_code == 200
    assert response_data["status_code"] == 200
    assert response_data["message"] == "FAQs retrieved successfully"
    assert response_data["data"] == {}
