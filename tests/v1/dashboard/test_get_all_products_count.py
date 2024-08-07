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


# Test for successful retrieve of products count
def test_get_products_count_successful(
    mock_db_session,
    test_user,
    access_token_user
):
    # Mock the query for getting user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    # Mock the query for products
    mock_db_session.query().all.return_value = [test_product]

    # Make request
    headers = {'Authorization': f'Bearer {access_token_user}'}
    response = client.get("/api/v1/dashboard/products/count", headers=headers)
    resp_d = response.json()
    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "Products count fetched successfully"
    assert resp_d['data']['count'] == 1


# Test for un-authenticated request
def test_for_unauthenticated_requests(
    mock_db_session,
    test_user
):
    # Mock the query for getting user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    # Make request || WRONG Authorization
    headers = {'Authorization': f'Bearer {random_access_token}'}
    response = client.get("/api/v1/dashboard/products/count", headers=headers)
    assert response.status_code == 401
    assert response.json()['message'] == "Could not validate credentials"

    # Make request || NO Authorization
    response = client.get("/api/v1/dashboard/products/count")
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

    mock_db_session.query().count.return_value = 0

    # Make request
    headers = {'Authorization': f'Bearer {access_token_user}'}
    response = client.get("/api/v1/dashboard/products/count", headers=headers)
    assert response.status_code == 404
    assert response.json()['message'] == "Products not found"
    assert not response.json().get('data')