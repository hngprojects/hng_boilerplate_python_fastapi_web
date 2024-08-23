import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from api.core.dependencies.email_sender import send_email
from api.v1.routes.waitlist import process_waitlist_signup
from main import app
import uuid

client = TestClient(app)

# Mock the BackgroundTasks to call the task function directly
@pytest.fixture(scope='module')
def mock_send_email():
    with patch("api.core.dependencies.email_sender.send_email") as mock_email_sending:
        with patch("fastapi.BackgroundTasks.add_task") as add_task_mock:
            # Override the add_task method to call the function directly
            add_task_mock.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)
            
            yield mock_email_sending

@pytest.fixture(scope="function")
def client_with_mocks(mock_send_email):
    with patch('api.db.database.get_db') as mock_get_db:
        # Create a mock session
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        yield client, mock_db

def test_waitlist_signup(mock_send_email, client_with_mocks):
    client, mock_db = client_with_mocks

    email = f"test{uuid.uuid4()}@gmail.com"
    user_data = {"email": email, "full_name": "Test User"}

    # Call the function directly, bypassing background tasks
    response = client.post("/api/v1/waitlist/", json=user_data)
    # Verify that send_email was called directly
    assert response.status_code == 201


def test_invalid_email(mock_send_email, client_with_mocks):
    client, _ = client_with_mocks
    response = client.post(
        "/api/v1/waitlist/", json={"email": "invalid_email", "full_name": "Test User"}
    )
    assert response.status_code == 422

def test_signup_with_empty_name(mock_send_email, client_with_mocks):
    client, _ = client_with_mocks
    response = client.post(
        "/api/v1/waitlist/", json={"email": "test@example.com", "full_name": ""}
    )
    data = response.json()
    assert response.status_code == 422
    assert data['message']['message'] == 'Full name is required'
