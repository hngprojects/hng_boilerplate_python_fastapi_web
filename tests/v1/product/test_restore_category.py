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


class TestRestoreProductCategory:
    @classmethod
    def setup_class(cls):
        # Override dependency to simulate an admin user
        app.dependency_overrides[user_service.get_current_user] = (
            lambda: get_admin_user()
        )

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_restore_category_authorized(self, mocker):
        # Arrange: Patch the restore method to return a dummy restored category
        dummy_category = {"name": "Category1", "is_deleted": False, "id": "1"}
        mocker.patch.object(
            ProductCategoryService,
            "restore_deleted",
            return_value=dummy_category,
        )

        # Act: Call the restore endpoint
        response = client.patch(
            "/api/v1/products/categories/Category1/restore"
        )

        # Assert: Check that the restore endpoint returns a 200 status and the expected response
        assert response.status_code == status.HTTP_200_OK
        json_data = response.json()
        assert json_data["data"] == dummy_category
        assert json_data["message"] == "Category restored successfully"

    def test_restore_category_unauthorized(self, mocker):
        # Arrange: Override dependency to simulate a non-admin user
        app.dependency_overrides[user_service.get_current_user] = (
            lambda: get_non_admin_user()
        )

        # Act: Attempt to restore a category
        response = client.patch(
            "/api/v1/products/categories/Category1/restore"
        )

        # Assert: The response should be 403 FORBIDDEN
        assert response.status_code == status.HTTP_403_FORBIDDEN
        json_data = response.json()
        assert (
            json_data["message"]
            == "User not authorized to perform this action"
        )

        # Restore dependency override for further tests
        app.dependency_overrides[user_service.get_current_user] = (
            lambda: get_admin_user()
        )
