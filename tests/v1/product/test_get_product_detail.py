import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from api.v1.models.organisation import Organisation
from api.v1.models.product import Product, ProductCategory
from api.v1.models.user import User
from main import app
from api.v1.routes.blog import get_db
from api.v1.services.user import user_service


# Mock database dependency
@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session


@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


# Mock user service dependency

user_id = uuid7()
org_id = uuid7()
product_id = uuid7()
category_id = uuid7()
timezone_offset = -8.0
tzinfo = timezone(timedelta(hours=timezone_offset))
timeinfo = datetime.now(tzinfo)
created_at = timeinfo
updated_at = timeinfo
access_token = user_service.create_access_token(str(user_id))
access_token2 = user_service.create_access_token(str(uuid7()))

# create test user

user = User(
    id=str(user_id),
    email="testuser@test.com",
    password="password123",
    created_at=created_at,
    updated_at=updated_at,
)

# Create test organisation

org = Organisation(
    id=str(org_id),
    name="hng",
    email=None,
    industry=None,
    type=None,
    country=None,
    state=None,
    address=None,
    description=None,
    created_at=created_at,
    updated_at=updated_at,
)

# Create test category

category = ProductCategory(id=category_id, name="Cat-1")

# Create test product

product = Product(
    id=str(product_id),
    name="prod one",
    description="Test product",
    price=125.55,
    org_id=str(org_id),
    quantity=50,
    image_url="http://img",
    category_id=str(category_id),
    status="in_stock",
    archived=False,
)


# user.organisation = org


def test_get_product_detail_success(client, db_session_mock):
    db_session_mock.query().filter().all.first.return_value = product
    headers = {"authorization": f"Bearer {access_token}"}

    response = client.get(
        f"/api/v1/organisations/{org_id}/products/{product_id}", headers=headers
    )

    assert response.status_code == 200


def test_get_product_detail_unauthenticated_user(client, db_session_mock):
    db_session_mock.query().filter().all.first.return_value = product
    response = client.get(f"/api/v1/organisations/{org_id}/products/{product_id}")

    assert response.status_code == 401
