from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from fastapi import HTTPException
from api.v1.services.product import ProductCategoryService
from api.v1.schemas.product import ProductCategoryRetrieve
from api.v1.services.user import user_service
from main import app

CATEGORY_DELETE_ENDPOINT = "/api/v1/products/categories/Category1"
client = TestClient(app)


def mock_deps():
    return MagicMock(id="user_id")


class TestDeleteProductCategory:

    @classmethod
    def setup_class(cls):
        # Override dependency to simulate an authenticated user
        app.dependency_overrides[user_service.get_current_user] = mock_deps

    @classmethod
    def teardown_class(cls):
        # Clear dependency overrides after tests
        app.dependency_overrides = {}

    # Test successful deletion of a product category
    def test_delete_product_category_successfully(self, mocker):
        # Create a mock deleted category object
        deleted_category = ProductCategoryRetrieve(name="Category1", id="1")

        # Patch the service method to return the mock deleted category
        mocker.patch.object(
            ProductCategoryService, "delete", return_value=deleted_category
        )

        response = client.delete("/api/v1/products/categories/Category1")
        assert response.status_code == 204
        assert response.json()["message"] == "Category deleted successfully"

    # Test deletion when the category does not exist
    def test_delete_product_category_not_found(self, mocker):
        # Patch the delete method to simulate a non-existent category
        def raise_not_found(*args, **kwargs):
            raise HTTPException(status_code=404, detail="Category not found.")

        mocker.patch.object(
            ProductCategoryService, "delete", side_effect=raise_not_found
        )

        response = client.delete(
            "/api/v1/products/categories/NonExistentCategory"
        )
        assert response.status_code == 404
        # For HTTPException responses, FastAPI returns the error in a
        # "message" field
        assert response.json()["message"] == "Category not found."

    # Test deletion when the user is unauthenticated
    def test_delete_product_category_unauthorized(self, mocker):
        # Remove dependency override to simulate an unauthenticated request
        app.dependency_overrides = {}
        response = client.delete("/api/v1/products/categories/Category1")
        assert response.status_code == 401
