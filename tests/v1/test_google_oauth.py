import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch
from requests.models import Response as RequestsResponse
from api.v1.models.user import User
from api.v1.schemas.google_oauth import OAuthToken
from main import app
from datetime import timedelta
from api.utils.success_response import success_response

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    db = Mock(spec=Session)
    yield db

@pytest.fixture
def mock_google_profile_response():
    profile_data = {
        "id": "123456789",
        "email": "test@example.com",
        "verified_email": True,
        "first_name": "Test User",
        "last_name": "Test",
        "family_name": "User",
        "picture": "https://example.com/avatar.jpg",
        "locale": "en"
    }
    response = Mock(spec=RequestsResponse)
    response.status_code = 200
    response.json.return_value = profile_data
    yield response

@pytest.fixture
def mock_google_services():
    with patch("api.v1.services.google_oauth.GoogleOauthServices.create") as mock_create_oauth_user:
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="Test User"
        )
        mock_create_oauth_user.return_value = mock_user
        yield mock_create_oauth_user

@pytest.fixture
def mock_user_services():
    with patch("api.v1.services.user.user_service.create_access_token") as mock_create_access_token, \
         patch("api.v1.services.user.user_service.create_refresh_token") as mock_create_refresh_token:
        mock_create_access_token.return_value = "access_token_example"
        mock_create_refresh_token.return_value = "refresh_token_example"
        yield mock_create_access_token, mock_create_refresh_token

@patch("requests.get")
def test_google_login(
    mock_requests_get, 
    mock_db_session, 
    mock_google_profile_response, 
    mock_google_services, 
    mock_user_services, 
    mock_send_email
):
    mock_requests_get.return_value = mock_google_profile_response
    
    token_request = OAuthToken(id_token="valid_token")
    response = client.post("api/v1/auth/google", json=token_request.dict(), headers={"Content-Type": "application/json"})
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Login successful"
    assert response_data["access_token"] == "access_token_example"
    assert response_data["data"]["user"]["email"] == "test@example.com"
    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] == "refresh_token_example"
