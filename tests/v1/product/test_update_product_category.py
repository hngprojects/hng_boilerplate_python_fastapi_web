from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from fastapi import HTTPException
from api.v1.services.product import ProductCategoryService
from api.v1.schemas.product import (
    ProductCategoryRetrieve,
)
from api.v1.services.user import user_service
from main import app

CATEGORY_UPDATE_ENDPOINT = "/api/v1/products/categories/Category1"
client = TestClient(app)


def mock_deps():
    return MagicMock(id="user_id")


class TestUpdateProductCategory:

    @classmethod
    def setup_class(cls):
        # Override dependency to simulate an authenticated user
        app.dependency_overrides[user_service.get_current_user] = mock_deps

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Test updating an existing product category successfully
    def test_update_product_category_successfully(self, mocker):
        # Prepare the update payload (e.g., update the category name)
        update_payload = {"name": "Updated Category1"}

        # Simulate the updated category as returned by the service
        updated_category = ProductCategoryRetrieve(
            name="Updated Category1", id="1"
        )

        # Patch the update method of the ProductCategoryService to return the
        # simulated updated category
        mocker.patch.object(
            ProductCategoryService, "update", return_value=updated_category
        )

        response = client.patch(
            "/api/v1/products/categories/Category1", json=update_payload
        )
        assert response.status_code == 200
        assert response.json()["data"] == {
            "name": "Updated Category1",
            "id": "1",
        }
        assert response.json()["message"] == "Category updated successfully"

    # Test updating a non-existent product category
    def test_update_product_category_not_found(self, mocker):
        update_payload = {"name": "Updated Category2"}

        # Patch the update method to raise a 404 HTTPException
        def raise_not_found(*args, **kwargs):
            raise HTTPException(status_code=404, detail="Category not found.")

        mocker.patch.object(
            ProductCategoryService, "update", side_effect=raise_not_found
        )

        response = client.patch(
            "/api/v1/products/categories/NonExistentCategory",
            json=update_payload,
        )
        assert response.status_code == 404
        assert response.json()["message"] == "Category not found."

    # Test update when the user is unauthenticated
    def test_update_product_category_unauthorized(self, mocker):
        # Remove dependency override to simulate an unauthenticated request
        app.dependency_overrides = {}

        update_payload = {"name": "Updated Category1"}
        response = client.patch(
            "/api/v1/products/categories/Category1", json=update_payload
        )
        assert response.status_code == 401
