import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from api.v1.schemas.product import ProductUpdate
from api.v1.models.product import Product
from api.v1.models.user import User
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from ...main import app
from api.v1.routes.blog import get_db



client = TestClient(app)

@pytest.mark.asyncio
@patch('api.v1.routes.product.get_current_user')
@patch('api.v1.routes.product.get_db')
async def test_update_product(mock_get_db, mock_get_current_user):
    # Create mock objects
    mock_db = MagicMock(Session)
    mock_user = User(id=1, username="testuser", email="testuser@example.com")

    # Set up mock return values
    mock_get_current_user.return_value = mock_user
    mock_get_db.return_value = mock_db

    # Define the product to be updated
    mock_product = Product(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        name="Old Product",
        price=100,
        description="Old Description",
        tag="Old Tag",
        updated_at=datetime.utcnow()
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_product

    # Define the update payload
    update_payload = ProductUpdate(
        product_name="New Product",
        price=150,
        description="New Description",
        tag="New Tag"
    )

    # Send the PUT request
    response = client.put(
        f"/product/{mock_product.id}",
        json=update_payload.dict()
    )

    # Assert response status and data
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == update_payload.product_name
    assert response_json["price"] == update_payload.price
    assert response_json["description"] == update_payload.description
    assert response_json["tag"] == update_payload.tag

    # Check database interactions
    mock_db.query.return_value.filter.return_value.first.assert_called_once()
    mock_db.add.assert_called_once_with(mock_product)
    mock_db.commit.assert_called_once()
