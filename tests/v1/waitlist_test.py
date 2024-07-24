import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import uuid

client = TestClient(app)

@pytest.fixture(scope="function")
def client_with_mocks():
    with patch('api.db.database.get_db') as mock_get_db:
        # Create a mock session
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        yield client, mock_db

def test_waitlist_signup(client_with_mocks):
    client, mock_db = client_with_mocks
    email = f"test{uuid.uuid4()}@gmail.com"
    response = client.post(
        "/api/v1/waitlist/", json={"email": email, "full_name": "Test User"}
    )
    assert response.status_code == 201
    assert response.json() == {"message": "You are all signed up!"}
   

def test_duplicate_email(client_with_mocks):
    client, mock_db = client_with_mocks
    # Simulate an existing user in the database
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

    client.post(
        "/api/v1/waitlist/", json={"email": "duplicate@gmail.com", "full_name": "Test User"}
    )
    response = client.post(
        "/api/v1/waitlist/", json={"email": "duplicate@gmail.com", "full_name": "Test User"}
    )
    data = response.json()
    print(response.status_code)
    assert response.status_code == 400
    assert data['success'] == False

def test_invalid_email(client_with_mocks):
    client, _ = client_with_mocks
    response = client.post(
        "/api/v1/waitlist/", json={"email": "invalid_email", "full_name": "Test User"}
    )
    data = response.json()
    assert response.status_code == 422
    assert data['message'] == 'Invalid input'

def test_signup_with_empty_name(client_with_mocks):
    client, _ = client_with_mocks
    response = client.post(
        "/api/v1/waitlist/", json={"email": "test@example.com", "full_name": ""}
    )
    data = response.json()
    assert response.status_code == 422
    assert data['message']['message'] == 'Full name is required'
