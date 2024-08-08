from datetime import datetime
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from jose import JWTError
import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.models.user import User
from api.v1.models.product import Product
from api.db.database import get_db
from api.v1.services.user import user_service
from uuid_extensions import uuid7

client = TestClient(app)
user_id = str(uuid7())
org_id = str(uuid7())


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."

    Yields:
        MagicMock: mock database
    """

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_success():
    with patch(
        "api.v1.services.product.ProductService.fetch_by_filter_status", autospec=True
    ) as mock_fetch_by_filter_status:
        mock_fetch_by_filter_status = []

        yield mock_fetch_by_filter_status


@pytest.mark.asyncio
async def test_get_products_by_filter_status(mock_db_session):
    access_token = user_service.create_access_token(str(user_id))
    response = client.get(
        "/api/v1/organisations/{org_id}/products/filter-status?filter_status=draft",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    # response = response.json()
    # assert response["message"] == "Products retrieved successfully"


# @pytest.mark.asyncio
# async def test_get_products_by_invalid_filter_status(mock_db_session):
#     access_token = user_service.create_access_token(str(user_id))
#     response = client.get(
#         "/api/v1/organisations/{org_id}/products/filter-status?filter_status=invalid_status",
#         headers={"Authorization": f"Bearer {access_token}"},
#     )

#     assert response.status_code == 422
#     response_json = response.json()
#     assert response_json["status_code"] == 422
