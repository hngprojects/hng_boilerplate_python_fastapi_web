import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from unittest.mock import MagicMock

client = TestClient(app)

mock_data = [
    {
        "client_name": "testclientname1",
        "author_id": "066a16d8-cab5-7dd3-8000-3a167556aa11",
        "content": "Amazing service!",
        "id": "066a6e8b-f008-7242-8000-8f090997001a",
        "updated_at": "2024-07-29T02:00:00.002967+01:00",
        "client_designation": "testclient",
        "comments": "Highly recommended!",
        "ratings": 4.8,
        "created_at": "2024-07-29T01:59:00.002967+01:00"
    },
    {
        "client_name": "testclientname2",
        "author_id": "066a16d8-cab5-7dd3-8000-3a167556ee55",
        "content": "Loved the service!",
        "id": "066a6e8b-f008-7242-8000-8f090997005e",
        "updated_at": "2024-07-29T02:20:10.002967+01:00",
        "client_designation": "testclient",
        "comments": "Best experience ever!",
        "ratings": 5.0,
        "created_at": "2024-07-29T02:18:00.002967+01:00"
    },
    {
        "client_name": "testclientname3",
        "author_id": "066a16d8-cab5-7dd3-8000-3a167556ff66",
        "content": "Decent service",
        "id": "066a6e8b-f008-7242-8000-8f090997006f",
        "updated_at": "2024-07-29T02:25:40.002967+01:00",
        "client_designation": "testclient",
        "comments": "Could be improved",
        "ratings": 4.2,
        "created_at": "2024-07-29T02:23:00.002967+01:00"
    },
]

"""Mocking The database"""
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}

def test_get_top_rated_testimonials(db_session_mock):

    mock_query = MagicMock()
    mock_query.count.return_value = len(mock_data)
    mock_query.offset.return_value.limit.return_value.all.return_value = mock_data

    db_session_mock.query.return_value = mock_query
    mock_query.order_by.return_value = mock_query

    url = 'api/v1/testimonials/top-rated'
    response = client.get(url, params={'page': 1, 'per_page': 2})

    assert response.status_code == 200
    assert response.json()['message'] == 'Successfully fetched items'

    returned_items = response.json()['data']['items']
    assert len(returned_items) == 3

    assert response.json()['data']['total'] == 3
    assert response.json()['data']['limit'] == 2
    assert response.json()['data']['skip'] == 0

    db_session_mock.query.assert_called()
    mock_query.order_by.assert_called()