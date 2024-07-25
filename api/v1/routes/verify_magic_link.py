from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
import pytest
from api.v1.routes.verify_magic_link import router
from api.v1.services.user import UserService

# Initialize FastAPI app and include the router
app = FastAPI()
app.include_router(router)

# Create a TestClient instance for making requests
client = TestClient(app)

@pytest.fixture
def mock_user_service(mocker):
    """Fixture to mock the UserService dependency."""
    mock_service = mocker.Mock()
    mock_service.verify_access_token.return_value = mocker.Mock(id=1)
    mock_service.create_access_token.return_value = "new_auth_token"
    return mock_service

def test_verify_magic_link_success(mocker, mock_user_service):
    """Test successful verification of the magic link."""
    # Mock the UserService methods
    mocker.patch.object(UserService, 'verify_access_token', return_value=mock_user_service.verify_access_token.return_value)
    mocker.patch.object(UserService, 'create_access_token', return_value=mock_user_service.create_access_token.return_value)

    # Simulate a successful token verification
    response = client.post("/auth/verify-magic-link", json={"token": "valid_token"})
    
    # Assert the response status code and content
    assert response.status_code == 200
    assert response.json() == {"auth_token": "new_auth_token", "status": 200}

def test_verify_magic_link_invalid_token(mocker, mock_user_service):
    """Test verification failure with an invalid token."""
    # Mock the UserService methods to simulate an invalid token scenario
    mocker.patch.object(UserService, 'verify_access_token', side_effect=HTTPException(status_code=400, detail="Invalid or expired token"))

    # Simulate a failed token verification
    response = client.post("/auth/verify-magic-link", json={"token": "invalid_token"})
    
    # Assert the response status code and content
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid or expired token"}
