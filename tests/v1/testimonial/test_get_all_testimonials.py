import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from unittest.mock import MagicMock

client = TestClient(app)

"""Mock data"""
data = [
     {
            "client_name": "testclientname",
            "author_id": "066a16d8-cab5-7dd3-8000-3a167556bb49",
            "content": "good testimonies",
            "id": "066a6e8b-f008-7242-8000-8f090997097c",
            "updated_at": "2024-07-29T01:56:31.002967+01:00",
            "client_designation": "testclient",
            "comments": "I love testimonies",
            "ratings": 5.02,
            "created_at": "2024-07-29T01:56:31.002967+01:00"
        },
      {
            "client_name": "testclientname",
            "author_id": "066a16d8-cab5-7dd3-8000-3a167556bb49",
            "content": "good testimonies",
            "id": "066a6e8b-f008-7242-8000-8f090997097c",
            "updated_at": "2024-07-29T01:56:31.002967+01:00",
            "client_designation": "testclient",
            "comments": "I love testimonies",
            "ratings": 5.02,
            "created_at": "2024-07-29T01:56:31.002967+01:00"
        },
         {
            "client_name": "testclientname",
            "author_id": "066a16d8-cab5-7dd3-8000-3a167556bb49",
            "content": "good testimonies",
            "id": "066a6e8b-f008-7242-8000-8f090997097c",
            "updated_at": "2024-07-29T01:56:31.002967+01:00",
            "client_designation": "testclient",
            "comments": "I love testimonies",
            "ratings": 5.02,
            "created_at": "2024-07-29T01:56:31.002967+01:00"
        },
         {
            "client_name": "testclientname",
            "author_id": "066a16d8-cab5-7dd3-8000-3a167556bb49",
            "content": "good testimonies",
            "id": "066a6e8b-f008-7242-8000-8f090997097c",
            "updated_at": "2024-07-29T01:56:31.002967+01:00",
            "client_designation": "testclient",
            "comments": "I love testimonies",
            "ratings": 5.02,
            "created_at": "2024-07-29T01:56:31.002967+01:00"
        },
         {
            "client_name": "testclientname",
            "author_id": "066a16d8-cab5-7dd3-8000-3a167556bb49",
            "content": "good testimonies",
            "id": "066a6e8b-f008-7242-8000-8f090997097c",
            "updated_at": "2024-07-29T01:56:31.002967+01:00",
            "client_designation": "testclient",
            "comments": "I love testimonies",
            "ratings": 5.02,
            "created_at": "2024-07-29T01:56:31.002967+01:00"
        }
]

"""Mocking The database"""
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield
    # Clean up after the test by removing the override
    app.dependency_overrides = {}

"""Testing the database"""
def test_get_testimonials(db_session_mock):
    db_session_mock.query().offset().limit().all.return_value = data

    url = 'api/v1/testimonials'
    mock_query = MagicMock()
    mock_query.count.return_value = 3
    db_session_mock.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = data

    db_session_mock.query.return_value = mock_query
    response = client.get(url, params={'page_size': 2, 'page': 1})
    assert len(response.json()['data']) == 5
    assert response.status_code == 200
    assert response.json()['message'] == 'Successfully fetched items'
