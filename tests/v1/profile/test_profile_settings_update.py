import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from main import app
from api.v1.schemas import UserAndProfileUpdate, success_response
from api.v1.models import User
from api.v1.services.user_service import get_current_user
from api.v1.routes.settings import update_profile_settings

# Create a TestClient instance for testing the FastAPI app
client = TestClient(app)

# Define a sample user and profile data
sample_user = {
    "id": "123",
    "username": "johndoe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "preferences": {"newsletter": True, "darkMode": False}
}

sample_user_and_profile_update = {
    "email": "new.email@example.com",
    "preferences": {"newsletter": False}
}

# Mock get_current_user to return a sample authenticated user
@patch("api.v1.services.user_service.get_current_user", return_value=sample_user)
# Mock get_db to provide a mock session
@patch("api.v1.routes.settings.get_db")
def test_update_profile_settings(mock_get_db, mock_get_current_user):
    # Mocking the db session and the update_user_and_profile function
    mock_session = MagicMock(spec=Session)
    mock_get_db.return_value = mock_session
    
    # Mock the update_user_and_profile function
    mock_session.query(User).filter_by().first.return_value = sample_user

    # Send the PATCH request to the endpoint
    response = client.patch(
        "/api/v1/users",
        json=sample_user_and_profile_update
    )

    # Assert the response status code and body
    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully"
    assert response.json()["user"]["email"] == sample_user_and_profile_update["email"]
    assert response.json()["user"]["preferences"]["newsletter"] == sample_user_and_profile_update["preferences"]["newsletter"]

def test_update_profile_user_not_found():
    # Mock get_current_user to return a sample authenticated user
    with patch("api.v1.services.user_service.get_current_user", return_value=sample_user):
        # Mock get_db to provide a mock session
        with patch("api.v1.routes.settings.get_db") as mock_get_db:
            mock_session = MagicMock(spec=Session)
            mock_get_db.return_value = mock_session

            # Simulate the user not being found in the database
            mock_session.query(User).filter_by().first.return_value = None

            # Send the PATCH request to the endpoint
            response = client.patch(
                "/api/v1/users",
                json=sample_user_and_profile_update
            )

            # Assert the response status code and body
            assert response.status_code == 404
            assert response.json()["detail"] == "User not found"
