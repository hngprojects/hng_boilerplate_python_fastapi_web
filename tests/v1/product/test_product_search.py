from datetime import datetime
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.models.user import User
from api.v1.models.product import Product
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.product import product_service
from uuid_extensions import uuid7

client = TestClient(app)
user_id = str(uuid7())
org_id = str(uuid7())


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_search_products():
    """Fixture to mock the search_products service function."""
    with patch("api.v1.services.product.product_service.search_products", autospec=True) as mock_search_products:
        yield mock_search_products


@pytest.mark.asyncio
async def test_search_products_success(mock_db_session, mock_search_products):

    mock_search_products.return_value = [
        {
            "id": str(uuid7()),
            "name": "Test Product",
            "description": "A test product",
            "price": 100.0,
            "category": "Test Category",
            "quantity": 10,
            "image_url": "http://example.com/image.jpg",
            "archived": False,
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    access_token = user_service.create_access_token(str(user_id))

    response = client.get(
        f"/api/v1/organisations/{org_id}/products/search?name=Test",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_products_no_results(mock_db_session, mock_search_products):

    mock_search_products.return_value = []
    access_token = user_service.create_access_token(str(user_id))

    response = client.get(
        f"/api/v1/organisations/{org_id}/products/search?name=NonExistentProduct",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_products_unauthorized(mock_db_session):

    response = client.get(
        f"/api/v1/organisations/{org_id}/products/search?name=Test")

    assert response.status_code == 401
