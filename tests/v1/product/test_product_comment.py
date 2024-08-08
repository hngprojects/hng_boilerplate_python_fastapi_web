import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from main import app
from sqlalchemy.orm import Session
from api.v1.services.product_comment import product_comment_service
from api.v1.models import User
from api.utils.dependencies import get_current_user
from api.v1.services.product_comment import ProductCommentService
from api.utils.success_response import success_response



client = TestClient(app)

@pytest.fixture
def mock_db():
    db = MagicMock(Session)
    yield db

@pytest.fixture
def mock_current_user():
    user = MagicMock(User)
    user.id = "test_user_id"
    return user

@pytest.fixture
def override_dependencies(mock_current_user):
    def _override_dependencies():
        app.dependency_overrides[product_comment_service] = MagicMock(ProductCommentService)
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
    _override_dependencies()
    yield
    app.dependency_overrides = {}



def test_get_product_comment(mock_db, override_dependencies):
    # Mock the ProductCommentService.fetch_single method
    mock_service = MagicMock(ProductCommentService)
    app.dependency_overrides[ProductCommentService] = lambda: mock_service
    mock_service.fetch_single.return_value = MagicMock(id="test_comment_id", content="Test content", author="Test author", user_id="test_user_id")

    response = client.get("/api/v1/products/test_product_id/comments/test_comment_id", params={"org_id": "test_org_id"})

    assert response.status_code == 200


