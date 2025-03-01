from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from fastapi import HTTPException

from api.db.database import get_db
from api.v1.models.contact_us import ContactUs
from api.v1.models.api_status import APIStatus
from api.v1.services.api_status import APIStatusService
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
        details="API not responding (HTTP 503)",
        last_checked=datetime.now(timezone.utc)
    )


@patch("api.v1.services.api_status.APIStatusService.upsert")
def test_post_api_status(mock_create, db_session_mock, client):
    """Tests the POST /api/v1/api-status endpoint to ensure successful posting of API status"""

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_create.return_value = mock_post_api_status()

    response = client.post('/api-status', json={
        "api_group": "Blog API",
        "status": "Down",
        "response_time": None,
        "details": "API not responding (HTTP 503)"
    })

    assert response.status_code == 201
    json_response = response.json()
    assert json_response["status"] == "success"
    assert json_response["status_code"] == 201
    assert json_response["message"] == "API Status created successfully"


@patch("api.v1.services.api_status.APIStatusService.fetch_all")
def test_get_api_status(mock_fetch, db_session_mock, client):
    """Tests the GET /api-status endpoint to ensure retrieval of API status"""

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_fetch.return_value = [mock_post_api_status()]  # Return a list for fetch_all

    response = client.get('/api-status')

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert json_response["status_code"] == 200
    assert json_response["message"] == "All API Status fetched successfully"


# New tests for PUT endpoint
def mock_updated_api_status():
    return APIStatus(
        id=str(uuid7()),
        api_group="Blog API",
        status="Up",
        response_time=200.0,
        details="API is running fine",
        last_checked=datetime.now(timezone.utc)
    )


@patch("api.v1.services.api_status.APIStatusService.update")
def test_put_api_status_success(mock_update, db_session_mock, client):
    """Tests the PUT /api/v1/api-status/{api_group} endpoint for successful update"""

    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_update.return_value = mock_updated_api_status()

    update_data = {
        "apiGroup": "Blog API",
        "status": "Up",
        "response_time": "200",
        "details": "API is running fine"
    }
    response = client.put('/api-status/Blog API', json=update_data)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert json_response["status_code"] == 200
    assert json_response["message"] == "API Status updated successfully"
    data = json_response["data"]
    assert data["api_group"] == "Blog API"
    assert data["status"] == "Up"
    assert float(data["response_time"]) == 200.0
    assert data["details"] == "API is running fine"


@patch("api.v1.services.api_status.APIStatusService.update")
def test_put_api_status_not_found(mock_update, db_session_mock, client):
    """Tests the PUT /api-status/{api_group} endpoint for a non-existent api_group"""

    mock_update.side_effect = APIStatusService.update.side_effect = HTTPException(
        status_code=404, detail="API Status not found"
    )

    update_data = {
        "apiGroup": "Nonexistent API",
        "status": "Up"
    }
    response = client.put('/api-status/Nonexistent API', json=update_data)

    assert response.status_code == 404
    json_response = response.json()
    assert json_response["status"] == "error"
    assert json_response["status_code"] == 404
    assert json_response["message"] == "API Status not found"
    assert json_response["data"] is None


@patch("api.v1.services.api_status.APIStatusService.update")
def test_put_api_status_partial_update(mock_update, db_session_mock, client):
    """Tests the PUT /api-status/{api_group} endpoint for partial update"""

    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    # Mock an updated status with only the status changed
    partial_updated_status = APIStatus(
        id=str(uuid7()),
        api_group="Blog API",
        status="Inactive",
        response_time=None,
        details="API not responding (HTTP 503)",
        last_checked=datetime.now(timezone.utc)
    )
    mock_update.return_value = partial_updated_status

    update_data = {
        "status": "Inactive"
    }
    response = client.put('/api-status/Blog API', json=update_data)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert json_response["status_code"] == 200
    assert json_response["message"] == "API Status updated successfully"
    data = json_response["data"]
    assert data["api_group"] == "Blog API"
    assert data["status"] == "Inactive"
    assert data["response_time"] is None
    assert data["details"] == "API not responding (HTTP 503)"


@patch("api.v1.services.api_status.APIStatusService.update")
def test_put_api_status_invalid_response_time(mock_update, db_session_mock, client):
    """Tests the PUT /api-status/{api_group} endpoint with invalid response_time"""

    mock_update.side_effect = HTTPException(
        status_code=500, detail="A database error occurred."
    )

    update_data = {
        "apiGroup": "Blog API",
        "status": "Up",
        "response_time": "invalid"
    }
    response = client.put('/api-status/Blog API', json=update_data)

    assert response.status_code == 500
    json_response = response.json()
    assert "A database error occurred" in json_response["detail"]