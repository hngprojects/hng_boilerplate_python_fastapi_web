import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Newsletter
from uuid_extensions import uuid7
from unittest.mock import MagicMock

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

# Test Newsletter
@pytest.fixture
def test_newsletter():
    return Newsletter(
        id=str(uuid7()), 
        title="test newsletter 1",
        description="a test newsletter"
        )



# Test fetch single newsletter
def test_fetching_single_newsletter(
    mock_db_session, 
    test_newsletter,
):
    # Mock the GET method for Newletter ID
    def mock_get(model, ident):
        if model == Newsletter and ident == test_newsletter.id:
            return test_newsletter
        return None

    mock_db_session.get.side_effect = mock_get

    # Test get single newsletter
    response = client.get(f"/api/v1/newsletters/{test_newsletter.id}")

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json()['message'] == "Successfully fetched newsletter"

