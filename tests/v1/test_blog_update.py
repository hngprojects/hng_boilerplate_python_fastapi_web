import pytest
from fastapi.testclient import TestClient
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from uuid import UUID


from main import app
from api.utils.dependencies import get_db, get_current_user
from api.v1.models.user import User
from api.v1.models.product import Product
from api.v1.schemas.product import ProductUpdate


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_db_session():
    db = MagicMock(spec=Session)
    yield db

@pytest.fixture
def current_user():
    return User(id=f'{uuid7()}', username="testuser", email="test@example.com", password="hashedpassword1", first_name="test", last_name="user")

@pytest.fixture
def valid_product_update():
    return ProductUpdate(product_name="Updated Product", price=150, description="Updated Description", tag="Updated Tag")

@pytest.fixture
def existing_product(mock_db_session, current_user):
    product = Product(id=f'{uuid7()}', name="Original Product", price=100, description="Original Description", tag="Original Tag", author_id=current_user.id)
    mock_db_session.query(Product).filter(Product.id == product.id).first.return_value = product
    return product

@pytest.mark.asyncio
async def test_update_product_success(client, mock_db_session, current_user, valid_product_update, existing_product):
    # Mock the dependencies
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: current_user

    response = client.put(f"/product/{existing_product.id}", json=valid_product_update.model_dump())

    assert response.status_code == 200
    assert response.json() == {
        "status": "200",
        "message": "Product updated successfully",
        "data": {"product": jsonable_encoder(existing_product)}
    }
    assert existing_product.name == valid_product_update.product_name
    assert existing_product.price == valid_product_update.price
    assert existing_product.description == valid_product_update.description
    assert existing_product.tag == valid_product_update.tag

@pytest.mark.asyncio
async def test_update_product_not_found(client, mock_db_session, current_user, valid_product_update):
    mock_db_session.query(Product).filter(Product.id == f'{uuid7()}').first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: current_user

    response = client.put(f"/product/{uuid7()}", json=valid_product_update.model_dump())

    assert response.status_code == 404
    assert response.json() == {'message': 'Product not Found', 'status_code': 404, 'success': False}

@pytest.mark.asyncio
async def test_update_product_forbidden(client, mock_db_session, current_user, valid_product_update, existing_product):
    # Simulate a different user
    different_user = User(id=f'{uuid7()}', username="otheruser", email="other@example.com", password="hashedpassword1", first_name="other", last_name="user")

    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: different_user

    response = client.put(f"/product/{existing_product.id}", json=valid_product_update.model_dump())

    assert response.status_code == 403
    assert response.json() == {'message': 'Not authorized to update this product', 'status_code': 403, 'success': False}

@pytest.mark.asyncio
async def test_update_product_empty_fields(client, mock_db_session, current_user, existing_product):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: current_user

    response = client.put(f"/product/{existing_product.id}", json={"product_name": "", "price": 0, "description": "", "tag": ""})

    assert response.status_code == 400
    assert response.json() == {'message': 'Product name, price, description, and tag cannot be empty', 'status_code': 400, 'success': False}

@pytest.mark.asyncio
async def test_update_product_internal_error(client, mock_db_session, current_user, valid_product_update, existing_product):
    # Simulate a database error
    mock_db_session.commit.side_effect = Exception("Database error")

    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: current_user

    response = client.put(f"/product/{existing_product.id}", json=valid_product_update.model_dump())

    assert response.status_code == 500
    assert response.json() == {'message': 'An error occurred while updating the product', 'status_code': 500, 'success': False}
