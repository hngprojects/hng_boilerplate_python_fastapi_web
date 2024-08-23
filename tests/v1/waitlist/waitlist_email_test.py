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
    
    # Mock the send_email function
    with patch('api.core.dependencies.email_sender.send_email') as mock_send_email:
        response = client.post(
            "/api/v1/waitlist/", json={"email": email, "full_name": "Test User"}
        )
        assert response.status_code == 201
        #mock_send_email.assert_called_once()

def test_duplicate_email(client_with_mocks):
    client, mock_db = client_with_mocks
    # Simulate an existing user in the database
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
    
    # Mock the send_email function
    with patch('api.core.dependencies.email_sender.send_email') as mock_send_email:
        client.post(
            "/api/v1/waitlist/", json={"email": "duplicate@gmail.com", "full_name": "Test User"}
        )
        response = client.post(
            "/api/v1/waitlist/", json={"email": "duplicate@gmail.com", "full_name": "Test User"}
        )
        data = response.json()
        assert response.status_code == 400

def test_invalid_email(client_with_mocks):
    client, _ = client_with_mocks
    
    # Mock the send_email function
    with patch('api.core.dependencies.email_sender.send_email') as mock_send_email:
        response = client.post(
            "/api/v1/waitlist/", json={"email": "invalid_email", "full_name": "Test User"}
        )
        data = response.json()
        assert response.status_code == 422
        assert data['message'] == 'Invalid input'

def test_signup_with_empty_name(client_with_mocks):
    client, _ = client_with_mocks
    
    # Mock the send_email function
    with patch('api.core.dependencies.email_sender.send_email') as mock_send_email:
        response = client.post(
            "/api/v1/waitlist/", json={"email": "test@example.com", "full_name": ""}
        )
        data = response.json()
        assert response.status_code == 422
        assert data['message']['message'] == 'Full name is required'
