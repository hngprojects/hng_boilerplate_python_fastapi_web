import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

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
async def test_delete_product_comment():
    # Mock data
    product_id = "test_product_id"
    comment_id = "test_comment_id"
    user_id = "test_user_id"
    
    # Mock database query
    db = override_get_db()
    mock_comment = ProductComment(id=comment_id, product_id=product_id, user_id=user_id)
    db.query(ProductComment).filter_by.return_value.first.return_value = mock_comment
    
    # Perform the request
    response = client.delete(f"/api/v1/products/{product_id}/comments/{comment_id}")
    
    # Assertions
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "status_code": 200,
        "message": "comment successfully deleted"
    }

