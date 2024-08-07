
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from jose import jwt
from datetime import datetime, timedelta

from api.v1.models import ProductComment, User
from api.v1.schemas.product import ProductDeletionResponse
from main import app
from api.db.database import get_db
from api.v1.services.product_comment import ProductCommentService
from api.v1.services.user import user_service

# Create a mock for the database dependency
def override_get_db():
    db = MagicMock()
    return db

app.dependency_overrides[get_db] = override_get_db

# Mock user service to return a test user
def mock_get_current_user():
    return User(id="test_user_id")

@pytest.fixture
def mock_token_verification():
    with patch("api.v1.services.user.UserService.verify_access_token") as mock:
        mock.return_value = MagicMock(id="test_user_id", is_super_admin=True)
        yield mock

app.dependency_overrides[user_service.get_current_user] = mock_get_current_user

# Mock the product comment service delete method
mock_product_comment_service = MagicMock(ProductCommentService)
mock_product_comment_service.delete.return_value = ProductDeletionResponse(
    status_code=200,
    status="success",
    message="comment successfully deleted"
)

app.dependency_overrides[ProductCommentService] = lambda: mock_product_comment_service

# Create a test client
client = TestClient(app)


@pytest.mark.asyncio
async def test_delete_product_comment(mock_token_verification):
    # Mock data
    product_id = "test_product_id"
    comment_id = "test_comment_id"
    user_id = "test_user_id"
    
    # Mock database query
    db = override_get_db()
    mock_comment = ProductComment(id=comment_id, product_id=product_id, user_id=user_id)
    db.query(ProductComment).filter_by.return_value.first.return_value = mock_comment
    
    # Create access token for the test user
    headers = {
        'Authorization': f'Bearer fake_token'
    }

    # Perform the request
    response = client.delete(f"/api/v1/products/{product_id}/comments/{comment_id}", headers=headers)
    
    # Log the response for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response JSON: {response.json()}")
    
    # Assertions
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "status_code": 200,
        "message": "comment successfully deleted"
    }
