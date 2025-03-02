import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from fastapi import status, HTTPException
from main import app
from api.v1.services.product import ProductCategoryService
from api.v1.services.user import user_service

client = TestClient(app)


# Dummy user objects for testing
def get_admin_user():
    user = MagicMock()
    user.is_superadmin = True
    return user


def get_non_admin_user():
    user = MagicMock()
    user.is_superadmin = False
    return user


class TestDeleteProductCategory:
    @classmethod
    def setup_class(cls):
        # For authorized tests, override the dependency to return an admin user.
        app.dependency_overrides[user_service.get_current_user] = (
            lambda: get_admin_user()
        )

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Soft Delete Tests
    def test_soft_delete_category_authorized(self, mocker):
        # Arrange: Patch the soft_delete method to return a dummy category dict.
        dummy_category = {"name": "Category1", "is_deleted": True, "id": "1"}
        mocker.patch.object(
            ProductCategoryService, "soft_delete", return_value=dummy_category
        )

        # Act: Call the soft delete endpoint.
        response = client.delete("/api/v1/products/categories/Category1")

        # Assert: Should succeed with a 200 status and expected response.
        assert response.status_code == status.HTTP_204_NO_CONTENT
        json_data = response.json()
        assert json_data["message"] == "Category deleted successfully"

    def test_soft_delete_category_unauthorized(self, mocker):
        # Arrange: Override dependency to simulate a non-admin user.
        app.dependency_overrides[user_service.get_current_user] = (
            lambda: get_non_admin_user()
        )

        # Act: Attempt to soft delete.
        response = client.delete("/api/v1/products/categories/Category1")

        # Assert: Should return 403 FORBIDDEN.
        assert response.status_code == status.HTTP_403_FORBIDDEN
        json_data = response.json()
        assert (
            json_data["message"]
            == "User not authorized to perform this action"
        )

        # Restore the dependency override.
        app.dependency_overrides[user_service.get_current_user] = (
            lambda: get_admin_user()
        )

    # Permanent Delete Tests
    def test_permanent_delete_category_authorized(self, mocker):
        # Arrange: Patch the permanent_delete method.
        dummy_category = {"name": "Category1", "id": "1"}
        mocker.patch.object(
            ProductCategoryService,
            "permanent_delete",
            return_value=dummy_category,
        )

        # Act: Call the permanent delete endpoint.
        response = client.delete(
            "/api/v1/products/categories/Category1/permanent"
        )

        # Assert: Should succeed with 200 OK and the expected response.
        assert response.status_code == status.HTTP_204_NO_CONTENT
        json_data = response.json()
        assert (
            json_data["message"] == "Category permanently deleted successfully"
        )

    def test_permanent_delete_category_unauthorized(self, mocker):
        # Arrange: Override dependency to simulate a non-admin user.
        app.dependency_overrides[user_service.get_current_user] = (
            lambda: get_non_admin_user()
        )

        # Act: Attempt permanent delete.
        response = client.delete(
            "/api/v1/products/categories/Category1/permanent"
        )

        # Assert: Should return 403 FORBIDDEN.
        assert response.status_code == status.HTTP_403_FORBIDDEN
        json_data = response.json()
        assert (
            json_data["message"]
            == "User not authorized to perform this action"
        )

        # Restore dependency override.
        app.dependency_overrides[user_service.get_current_user] = (
            lambda: get_admin_user()
        )
