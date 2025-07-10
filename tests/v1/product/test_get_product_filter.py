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

# Create test user

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

category = ProductCategory(id=category_id, name="Electronics")

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


# Mock data for multiple products
products = [
    Product(
        id=str(uuid7()),
        name="Smartphone",
        description="A smartphone",
        price=500.00,
        org_id=str(org_id),
        quantity=10,
        image_url="http://img1",
        category_id=str(category_id),
        status="in_stock",
        archived=False,
    ),
    Product(
        id=str(uuid7()),
        name="Laptop",
        description="A laptop",
        price=1200.00,
        org_id=str(org_id),
        quantity=5,
        image_url="http://img2",
        category_id=str(category_id),
        status="in_stock",
        archived=False,
    ),
    Product(
        id=str(uuid7()),
        name="T-Shirt",
        description="A T-Shirt",
        price=20.00,
        org_id=str(org_id),
        quantity=100,
        image_url="http://img3",
        category_id=str(uuid7()),  # Different category
        status="in_stock",
        archived=False,
    ),
]


def test_get_products_filtered_by_category(client, db_session_mock):
    # Mock the database query to return filtered products
    db_session_mock.query().join().filter().offset().limit().all.return_value = [
        products[0], products[1]]
    db_session_mock.query().join().filter().count.return_value = 2  # Return an integer

    headers = {"authorization": f"Bearer {access_token}"}
    response = client.get(
        "/api/v1/products?category=Electronics",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["items"]) == 2


def test_get_all_products_without_filter(client, db_session_mock):
    # Mock the database query to return all products
    db_session_mock.query().offset().limit().all.return_value = products
    db_session_mock.query().count.return_value = 3

    headers = {"authorization": f"Bearer {access_token}"}
    response = client.get(
        "/api/v1/products",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["items"]) == 3


def test_unauthorized_access(client, db_session_mock):
    # Test unauthorized access (missing or invalid token)
    response = client.get("/api/v1/products")
    assert response.status_code == 401
    assert response.json() == {
        "status": False,
        "status_code": 401,
        "message": "Not authenticated"
    }


def test_invalid_category_name(client, db_session_mock):
    # Mock the database query to return no products for an invalid category
    db_session_mock.query().join().filter().offset().limit().all.return_value = []
    db_session_mock.query().join().filter().count.return_value = 0  # Return an integer

    headers = {"authorization": f"Bearer {access_token}"}
    response = client.get(
        "/api/v1/products?category=InvalidCategory",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["items"]) == 0


def test_empty_results_for_valid_category(client, db_session_mock):
    # Mock the database query to return no products for a valid but unused category
    db_session_mock.query().join().filter().offset().limit().all.return_value = []
    db_session_mock.query().join().filter().count.return_value = 0  # Return an integer

    headers = {"authorization": f"Bearer {access_token}"}
    response = client.get(
        "/api/v1/products?category=Furniture",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["items"]) == 0
