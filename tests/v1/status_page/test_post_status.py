from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.contact_us import ContactUs
from api.v1.models.api_status import APIStatus
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


def mock_post_api_status():
    return APIStatus(
        id=str(uuid7()), 
        api_group="Blog API",
        status="Down",
        response_time=None,
        details="API not responding (HTTP 503)"
    )


@patch("api.v1.services.api_status.APIStatusService.upsert")
def test_post_api_status(mock_create, db_session_mock, client):
    """Tests the POST /api/v1/api-status endpoint to ensure successful posting of API status"""

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_create.return_value = mock_post_api_status()
    # mock_check_existing.return_value = None

    response = client.post('/api/v1/api-status', json={
        "api_group": "Blog API",
        "status": "Down",
        "response_time": None,
        "details": "API not responding (HTTP 503)"
    })

    assert response.status_code == 201

@patch("api.v1.services.api_status.APIStatusService.fetch_all")
def test_get_api_status(mock_fetch, db_session_mock, client):
    """Tests the GET /api/v1/api-status endpoint to ensure retrieval of API status"""

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_fetch.return_value = mock_post_api_status()

    response = client.get('/api/v1/api-status')

    print(response.json())
    assert response.status_code == 200
