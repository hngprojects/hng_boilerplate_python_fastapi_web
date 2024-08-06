import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User

client = TestClient(app)

@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com")

@patch("api.v1.routes.profiles.Image.open")
@patch("api.v1.routes.profiles.os.makedirs")
@patch("builtins.open", new_callable=MagicMock)
def test_upload_profile_image(mock_open, mock_makedirs, mock_image_open, mock_user):
    # Setup mocks
    mock_image = MagicMock()
    mock_image_open.return_value = mock_image
    mock_image.resize.return_value = mock_image
    mock_image.save = MagicMock()

    # Mock current user dependency
    with patch("api.utils.dependencies.get_current_user", return_value=mock_user):
        response = client.post(
            "/api/v1/profile/upload-image",
            files={"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")}
        )

    # Check response
    assert response.status_code == 200
    assert response.json()["message"] == "Image uploaded successfully"
    assert "image_url" in response.json()

