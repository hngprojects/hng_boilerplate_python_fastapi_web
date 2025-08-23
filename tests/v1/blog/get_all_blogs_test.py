from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.v1.routes.blog import get_db
from main import app

# Mock database dependency
@pytest.fixture
def db_session_mock():
    return MagicMock(spec=Session)

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_get_all_blogs_empty(client, db_session_mock):
    mock_query = MagicMock()
    mock_query.count.return_value = 0
    mock_query.all.return_value = []

    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    db_session_mock.query.return_value = mock_query

    response = client.get("/api/v1/blogs")

    assert response.status_code == 200
    assert response.json()["data"]["items"] == []

def test_get_all_blogs_with_data(client, db_session_mock):
    mock_blog_data = [
        {"id": "123", "title": "Test Blog", "content": "Test Content"}
    ]
    
    mock_query = MagicMock()
    mock_query.count.return_value = 1
    mock_query.all.return_value = mock_blog_data

    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    db_session_mock.query.return_value = mock_query

    response = client.get("/api/v1/blogs")

    assert response.status_code == 200
    assert len(response.json()["data"]["items"]) >= 1