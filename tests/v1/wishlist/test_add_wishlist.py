import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.v1.models.user import User
from main import app
from api.v1.services.wishlist import wishlist_service
from api.v1.services.user import user_service, UserService
from api.v1.services.wishlist import ProductNotFoundException, ProductAlreadyInWishlistException


@pytest.fixture
def client():
	return TestClient(app)

@pytest.fixture
def auth_headers():
	return {"Authorization": "Bearer test-token"}


# def mock_current_user():
# 	return MagicMock(id="test-user-id")


class TestAddToWishlist:
	@classmethod
	def setup_class(cls):
		app.dependency_overrides[user_service.get_current_user] = lambda: User(
		id="test-user-id",
		email="test@example.com",
		password="hashedpassword",
		is_active=True
	)

	@classmethod
	def teardown_class(cls):
		app.dependency_overrides.pop(user_service.get_current_user, None)

	def test_add_to_wishlist_unauthorized(self, client):
		app.dependency_overrides[user_service.get_current_user] = lambda: None

		response = client.post("/api/v1/wishlist/", json={"product_id": "test-product-id"}, headers={})

		app.dependency_overrides[user_service.get_current_user] = lambda: User(
			id="test-user-id",
			email="test@example.com",
			password="hashedpassword",
			is_active=True
		)

		assert response.status_code == 401

	def test_add_to_wishlist_missing_product_id(self, client, auth_headers):
		response = client.post("/api/v1/wishlist/", json={}, headers=auth_headers)
		assert response.status_code == 422

	
	@patch('api.v1.services.wishlist.wishlist_service.create')
	def test_add_to_wishlist_success(self, mock_create, client, auth_headers):
		mock_create.return_value = {"id":"wishlist-id", "user_id":"test-user-id", "product_id":"test-product-id"}

		response = client.post("/api/v1/wishlist/", json={"product_id": "test-product-id"}, headers=auth_headers)

		assert response.status_code == 201
		assert response.json()["message"] == "Product added to wishlist successfully"

	
	@patch('api.v1.services.wishlist.wishlist_service.create')
	def test_add_to_wishlist_product_not_found(self, mock_create, client, auth_headers):
		mock_create.side_effect = ProductNotFoundException("Product not found")
		
		response = client.post("/api/v1/wishlist/", json={"product_id": "invalid-product-id"}, headers=auth_headers)
		
		assert response.status_code == 404


	@patch('api.v1.services.wishlist.wishlist_service.create')
	def test_add_to_wishlist_already_exists(self, mock_create, client, auth_headers):
		mock_create.side_effect = ProductAlreadyInWishlistException("Product already in wishlist")
		
		response = client.post("/api/v1/wishlist/", json={"product_id": "test-product-id"}, headers=auth_headers)
		
		assert response.status_code == 400
