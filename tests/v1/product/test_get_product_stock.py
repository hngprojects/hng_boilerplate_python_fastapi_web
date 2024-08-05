import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from api.v1.models.product import Product
from api.v1.services.product import product_service
from datetime import datetime
from unittest.mock import MagicMock
from uuid_extensions import uuid7
from uuid import uuid4
from api.v1.services.user import user_service
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

client = TestClient(app)


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_current_user():
    return {"id": str(uuid7()), "email": "testuser@gmail.com"}


@pytest.fixture
def mock_non_member_user():
    return {"id": str(uuid4()), "email": "nonmemberuser@gmail.com"}


@pytest.fixture
def mock_get_current_user(mock_current_user):
    async def mock_get_current_user():
        return mock_current_user
    return mock_get_current_user


@pytest.fixture
def mock_get_non_member_user(mock_non_member_user):
    async def mock_get_non_member_user():
        return mock_non_member_user
    return mock_get_non_member_user


@pytest.fixture
def mock_product():
    return Product(
        id=str(uuid7()),
        name="Test Product",
        updated_at=datetime.utcnow(),
        org_id=str(uuid7()),
        quantity=15
    )


@pytest.fixture
def access_token(mock_current_user):
    return user_service.create_access_token(user_id=mock_current_user["id"])


@pytest.fixture
def access_token_2(mock_non_member_user):
    return user_service.create_access_token(user_id=mock_non_member_user["id"])


def test_get_product_stock(mock_db, mock_get_current_user, mock_product, access_token, monkeypatch):
    # Mock the product_service.fetch_stock method
    def mock_fetch_stock(db, product_id, mock_get_current_user):
        if product_id == mock_product.id:
            return {
                "product_id": mock_product.id,
                "current_stock": mock_product.quantity,
                "last_updated": mock_product.updated_at
            }
        else:
            return None

    def mock_check_user_in_org(user, organization):
        return True

    monkeypatch.setattr(product_service, "fetch_stock", mock_fetch_stock)
    monkeypatch.setattr(
        "api.utils.db_validators.check_user_in_org", mock_check_user_in_org)

    monkeypatch.setattr(
        "api.v1.services.user.user_service.get_current_user", mock_get_current_user
    )

    response = client.get(
        f"/api/v1/products/{mock_product.id}/stock",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200


def test_get_product_stock_not_found(mock_db, mock_get_current_user, access_token, monkeypatch):

    response = client.get(
        f"/api/v1/products/1/stock",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404


def test_get_product_stock_forbidden(mock_db, mock_get_non_member_user, mock_product, access_token_2, monkeypatch):
    # Mock the product_service.fetch_stock method
    def mock_fetch_stock(db, product_id):
        return mock_product

    def mock_check_user_in_org(user, organization):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this organization",
        )

    user = mock_get_non_member_user()

    try:
        mock_check_user_in_org(user, mock_product.org_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    monkeypatch.setattr(product_service, "fetch_stock", mock_fetch_stock)
    monkeypatch.setattr(
        "api.utils.db_validators.check_user_in_org", mock_check_user_in_org
    )
    monkeypatch.setattr(
        "api.v1.services.user.user_service.get_current_user", mock_get_non_member_user
    )

    response = client.get(
        f"/api/v1/products/{mock_product.id}/stock",
        headers={"Authorization": f"Bearer {access_token_2}"}
    )

    assert response.status_code == 400


def test_get_product_stock_unauthorized(mock_db, monkeypatch):
    async def mock_get_current_user():
        raise ValueError("Unauthorized")
    monkeypatch.setattr(
        "api.v1.services.user.user_service.get_current_user", mock_get_current_user
    )

    response = client.get(f"/api/v1/products/{str(uuid7())}/stock")

    assert response.status_code == 401
