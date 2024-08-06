import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service
from uuid_extensions import uuid7

client = TestClient(app)
user_id = str(uuid7())

@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com")

@patch("api.v1.routes.profile.Image.open")
@patch("api.v1.routes.profile.os.makedirs")
@patch("builtins.open", new_callable=MagicMock)
def test_upload_profile_image(mock_open, mock_makedirs, mock_image_open, mock_user):
    
    access_token = user_service.create_access_token(str(user_id))
    mock_image = MagicMock()
    mock_image_open.return_value = mock_image
    mock_image.resize.return_value = mock_image
    mock_image.save = MagicMock()

    with patch("api.v1.routes.profile.user_service.get_current_user", return_value=mock_user):
        response = client.post(
            "/profile/upload-image",
            headers={'Authorization': f'Bearer {access_token}'},
            files={"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")}
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Image uploaded successfully"
    assert "image_url" in response.json()
