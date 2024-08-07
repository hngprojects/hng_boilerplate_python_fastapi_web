import pytest
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User, Product, ProductCategory, Organization

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

@pytest.fixture
def mock_user_service():
    with patch("api.v1.services.user.user_service", autospec=True) as user_service_mock:
        yield user_service_mock

@pytest.fixture
def mock_product_service():
    with patch("api.v1.services.product.product_service", autospec=True) as product_service_mock:
        yield product_service_mock

# Test User
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
        is_super_admin=True
    )


@pytest.fixture()
def test_category():
    prod_category = ProductCategory(
        id=str(uuid7()),
        name="Category 1"
    )
    return prod_category


@pytest.fixture()
def test_org():
    org = Organization(
        id=str(uuid7()),
        name="Organization 1"
    )
    return org


@pytest.fixture()
def test_product(test_category, test_org):
    product = Product(
        id=str(uuid7()),
        name="Product 1",
        description="Description for product 1",
        price=19.99,
        org_id=test_org.id,
        category_id=test_category.id,
        image_url="random.com",
        quantity=200,
        created_at=datetime.now(timezone.utc)
    )
    product.category = test_category
    product.organization = test_org
    return product


@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)

@pytest.fixture
def random_access_token():
    return user_service.create_access_token(user_id=str(uuid7()))


# Test for successful retrieve of products
def test_get_products_successful(
    mock_db_session,
    test_user,
    test_org,
    test_product,
    test_category,
    access_token_user
):
    # Mock the query for getting user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    # TEST A SINGLE PRODUCT FOR 1-PAGE RESULT #

    # Mock the query for products
    mock_db_session.query().count.return_value = 1
    mock_db_session.query().all.return_value = [test_product]

    # Make request
    headers = {'Authorization': f'Bearer {access_token_user}'}
    response = client.get("/api/v1/dashboard/products", headers=headers)
    resp_d = response.json()

    print(resp_d)
    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "Products fetched successfully"

    pagination = resp_d['data']['pagination']
    assert pagination['pages'] == 1
    assert pagination['limit'] == 10
    assert pagination['offset'] == 0
    assert pagination['total_items'] == 1

    products = resp_d['data']['products']
    assert len(products) == 1

    prod = products[0]
    assert prod['id'] == test_product.id
    assert prod['name'] == test_product.name
    assert prod['description'] == test_product.description
    assert float(prod['price']) == test_product.price
    assert float(prod['quantity']) == test_product.quantity
    assert prod['image_url'] == test_product.image_url
    assert prod['archived'] == test_product.archived
    assert prod['category_name'] == test_category.name
    assert prod['organization_name'] == test_org.name
    assert prod['category_id'] == test_category.id
    assert prod['organization_id'] == test_org.id
    assert datetime.fromisoformat(prod['created_at']) == test_product.created_at

    # RESET MOCK PRODUCTS TO SIMULATE MULTI-PAGE RESULT #

    # Mock the query for products, this time for 5 products
    five_products = [test_product, test_product, test_product, test_product, test_product]
    mock_db_session.query().all.return_value = five_products

    # Make request
    response = client.get("/api/v1/dashboard/products", headers=headers)

    resp_d = response.json()

    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "Products fetched successfully"

    pagination = resp_d['data']['pagination']
    assert pagination['pages'] == 1
    assert pagination['limit'] == 10
    assert pagination['offset'] == 0
    assert pagination['total_items'] == 5

    products = resp_d['data']['products']
    assert len(products) == 5


# Test for un-authenticated request
def test_for_unauthenticated_requests(
    mock_db_session,
    test_user
):
    # Mock the query for getting user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    # Make request || WRONG Authorization
    headers = {'Authorization': f'Bearer {random_access_token}'}
    response = client.get("/api/v1/dashboard/products", headers=headers)
    assert response.status_code == 401
    assert response.json()['message'] == "Could not validate credentials"

    # Make request || NO Authorization
    response = client.get("/api/v1/dashboard/products")
    assert response.status_code == 401
    assert response.json()['message'] == "Not authenticated"


# Test for no product 
def test_for_products_not_found(
    mock_db_session,
    test_user,
    access_token_user
):
    # Mock the query for getting user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    mock_db_session.query().all.return_value = []

    # Make request
    headers = {'Authorization': f'Bearer {access_token_user}'}
    response = client.get("/api/v1/dashboard/products", headers=headers)
    assert response.status_code == 404
    assert response.json()['message'] == "Products not found"
    assert not response.json().get('data')
