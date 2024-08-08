import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from unittest.mock import MagicMock, patch
from api.v1.models import TermsAndConditions, User
from api.v1.services.terms_and_conditions import terms_and_conditions_service
from uuid_extensions import uuid7
from fastapi import status

client = TestClient(app)
URI = "/api/v1/terms-and-conditions"

test_data = {
    "id": str(uuid7()),
    "title": "My Terms and Conditions",
    "content": "My Content",
}

@pytest.fixture
def mock_db_session(_=MagicMock()):
    """Mock session"""
    with patch(get_db.__module__):
        app.dependency_overrides[get_db] = lambda: _
        yield _
    app.dependency_overrides = {}

def create_mock_terms_and_conditions(_):
    """Mock terms and conditions"""
    _.query.return_value.filter.return_value.first.return_value = TermsAndConditions(
        id=test_data["id"],
        title=test_data["title"],
        content=test_data["content"],
    )

@pytest.mark.usefixtures("mock_db_session")
def test_get_terms_and_conditions(mock_db_session):
    """Test get terms and conditions by ID"""
    # Create mock data
    create_mock_terms_and_conditions(mock_db_session)
    
    # Perform the GET request
    res = client.get(f"{URI}/{test_data['id']}")
    
    # Assert the response status code is 200 OK
    assert res.status_code == status.HTTP_200_OK
    
    # Assert the response data matches the mock data
    assert res.json()["data"]["id"] == test_data["id"]
    assert res.json()["data"]["title"] == test_data["title"]
    assert res.json()["data"]["content"] == test_data["content"]

def create_mock_empty_terms_and_conditions(_):
    """Mock no terms and conditions found"""
    _.query.return_value.filter.return_value.first.return_value = None

@pytest.mark.usefixtures("mock_db_session")
def test_get_terms_and_conditions_not_found(mock_db_session):
    """Test get terms and conditions by ID when not found"""
    # Mock no data found
    create_mock_empty_terms_and_conditions(mock_db_session)
    
    # Perform the GET request with a non-existent ID
    res = client.get(f"{URI}/{str(uuid7())}")
    
    # Assert the response status code is 404 Not Found
    assert res.status_code == status.HTTP_404_NOT_FOUND
    
    # Assert the response message is correct
    assert res.json()["message"] == "Term and condition not found"
