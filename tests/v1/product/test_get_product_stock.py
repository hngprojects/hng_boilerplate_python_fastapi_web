import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from api.v1.models.product import Product
from api.v1.services.product import product_service
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from uuid import uuid4
from api.v1.services.user import user_service
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

client = TestClient(app)


@pytest.fixture(scope="function")
def mock_db_product():
    return MagicMock(spec=Session)


@pytest.fixture(scope="function")
def mock_current_user_product():
    return {"id": str(uuid7()), "email": "testuser@gmail.com"}


@pytest.fixture(scope="function")
def mock_non_member_user_product():
    return {"id": str(uuid4()), "email": "nonmemberuser@gmail.com"}


@pytest.fixture(scope="function")
def mock_get_current_user_product(mock_current_user_product):
    async def mock_get_current_user():
        return mock_current_user_product

    return mock_get_current_user


@pytest.fixture(scope="function")
def mock_get_non_member_user_product(mock_non_member_user_product):
    async def mock_get_non_member_user():
        return mock_non_member_user_product

    return mock_get_non_member_user


@pytest.fixture(scope="function")
def mock_product():
    return Product(
        id=str(uuid7()),
        name="Test Product",
        updated_at=datetime.utcnow(),
        org_id=str(uuid7()),
        quantity=15,
    )


@pytest.fixture(scope="function")
def access_token_product(mock_current_user_product):
    return user_service.create_access_token(user_id=mock_current_user_product["id"])


org_id = str(uuid7())
product_id = str(uuid7())


@pytest.mark.asyncio
async def test_get_product_stock(
    mock_db_product,
    mock_get_current_user_product,
    mock_product,
    access_token_product,
    monkeypatch,
):
    def mock_fetch_stock(db, product_id, current_user, org_id):
        if product_id == mock_product.id:
            return {
                "product_id": mock_product.id,
                "current_stock": mock_product.quantity,
                "last_updated": mock_product.updated_at,
            }
        else:
            return None

    def mock_check_user_in_org(user, organisation):
        return True

    with patch.object(product_service, "fetch_stock", mock_fetch_stock):
        with patch("api.utils.db_validators.check_user_in_org", mock_check_user_in_org):
            with patch(
                "api.v1.services.user.user_service.get_current_user",
                mock_get_current_user_product,
            ):
                response = client.get(
                    f"/api/v1/organisations/{org_id}/products/{mock_product.id}/stock",
                    headers={"Authorization": f"Bearer {access_token_product}"},
                )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_product_stock_not_found(
    mock_db_product, mock_get_current_user_product, access_token_product, monkeypatch
):
    with patch(
        "api.v1.services.user.user_service.get_current_user",
        mock_get_current_user_product,
    ):
        response = client.get(
            f"/api/v1/organisations/{org_id}/products/1/stock",
            headers={"Authorization": f"Bearer {access_token_product}"},
        )

    assert response.status_code == 404


# @pytest.mark.asyncio
# async def test_get_product_stock_forbidden(mock_db_product, mock_get_non_member_user_product, mock_product, monkeypatch):
#     def mock_fetch_stock(db, product_id):
#         return mock_product

#     def mock_check_user_in_org(user, organisation):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="You are not a member of this organisation",
#         )

#     user = await mock_get_non_member_user_product()

#     with patch.object(product_service, "fetch_stock", mock_fetch_stock):
#         with patch("api.utils.db_validators.check_user_in_org", mock_check_user_in_org):
#             with patch("api.v1.services.user.user_service.get_current_user", return_value=user):
#                 response = client.get(
#                     f"/api/v1/products/{mock_product.id}/stock",
#                     headers={"Authorization": "Bearer dummy_token"}
#                 )

#     assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_product_stock_unauthorized(mock_db_product, monkeypatch):
    async def mock_get_current_user():
        raise ValueError("Unauthorized")

    with patch(
        "api.v1.services.user.user_service.get_current_user", mock_get_current_user
    ):
        response = client.get(
            f"/api/v1/organisations/{org_id}/products/{product_id}/stock"
        )

    assert response.status_code == 401
