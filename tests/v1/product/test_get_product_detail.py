import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from api.v1.models.organization import Organization
from api.v1.models.product import Product, ProductCategory
from ....main import app
from api.v1.routes.blog import get_db
from api.v1.services.user import user_service
from api.v1.services.product import product_service


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

# Create test organization

org = Organization(
    id=str(org_id),
    company_name="hng",
    company_email=None,
    industry=None,
    organization_type=None,
    country=None,
    state=None,
    address=None,
    lga=None,
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
product.organization = org
product.category = category
product.variants = []

@pytest.fixture
def mock_product_service_fetch(db_session_mock):
    with patch.object(product_service, 'fetch', return_value=product) as mock:
        yield mock


def test_get_product_detail_success(
    client, db_session_mock, mock_product_service_fetch
):
    headers = {"authorization": f"Bearer {access_token}"}

    response = client.get(f"/api/v1/products/{product_id}", headers=headers)
    data = response.json()["data"]

    assert response.status_code == 200
    assert isinstance(data["organization"], dict)
    assert "id" in data["organization"].keys()
    assert "company_name" in data["organization"].keys()
    assert "company_email" in data["organization"].keys()
    assert "industry" in data["organization"].keys()
    assert "organization_type" in data["organization"].keys()
    assert "country" in data["organization"].keys()
    assert "state" in data["organization"].keys()
    assert "address" in data["organization"].keys()
    assert "lga" in data["organization"].keys()
    assert isinstance(data["variants"], list)


def test_get_proudct_detail_unauthenticated_user(client, db_session_mock):
    db_session_mock.query().filter().all.first.return_value = product
    response = client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 401
