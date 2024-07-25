import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from api.utils.dependencies import get_current_user
from datetime import datetime
from fastapi import HTTPException
from api.v1.models.product import Product
from api.v1.models.user import User
from jose import JWTError

client = TestClient(app)

@pytest.fixture
def mock_db(mocker):
    mock_db = mocker.patch('api.db.database.get_db', return_value=MagicMock())
    yield mock_db
    
@pytest.fixture
def mock_get_current_user(mocker):
    user = User(id='user_id', is_super_admin=False)
    mock = mocker.patch('api.utils.dependencies.get_current_user', return_value=user)
    print(f"Mock get_current_user setup: {user.id}, {user.is_super_admin}")
    return mock

def test_get_current_user_mock(mock_get_current_user):
    user = mock_get_current_user.return_value
    print(f"User returned by mock_get_current_user: {user.id}, {user.is_super_admin}")
    assert user.id == 'user_id'
    assert not user.is_super_admin

def test_update_product_with_valid_token(mock_db, mock_get_current_user, mocker):
    mocker.patch('jwt.decode', return_value={"user_id": "user_id"})  
    
    print(f"Mocked get_current_user: {mock_get_current_user}")
        
    mock_product = MagicMock()
    mock_product.id = 'e65c9f26-696a-42df-a4b9-4da214267'
    mock_product.name = 'Old Product'
    mock_product.price = 20.0
    mock_product.description = 'Old Description'
    mock_product.updated_at = None

    mock_db().query().filter().first.return_value = mock_product

    def mock_commit():
        mock_product.updated_at = datetime.utcnow()

    mock_db().commit = mock_commit

    product_update = {
        "name": "Updated Product",
        "price": 25.0,
        "description": "Updated Description",
    }

    response = client.put(
        "/api/v1/product/e65c9f26-696a-42df-a4b9-4da214267",
        json=product_update,
        headers={"Authorization": "Bearer valid_token"}
    )

    print(f"Response JSON: {response.json()}")
    print(f"Mocked user: {mock_get_current_user.return_value.id}, {mock_get_current_user.return_value.is_super_admin}")
    
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Product"
    assert response.json()["price"] == 25.0
    assert response.json()["description"] == "Updated Description"
    assert response.json()["updated_at"] is not None

def test_update_product_with_invalid_token(mock_db, mocker):
    mocker.patch('jwt.decode', side_effect=JWTError("Invalid token"))

    mocker.patch('api.utils.dependencies.get_current_user', side_effect=HTTPException(status_code=401, detail="Invalid credentials"))
    
    response = client.put(
        "/api/v1/product/e65c9f26-696a-42df-a4b9-4da214267",
        json={"name": "Product"},
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_update_product_with_missing_fields(mock_db, mock_get_current_user, mocker):
    mocker.patch('jwt.decode', return_value={"user_id": "user_id"})  
    
    response = client.put(
        "/api/v1/product/e65c9f26-696a-42df-a4b9-4da214267",
        json={},
        headers={"Authorization": "Bearer valid_token"}
    )
    
    print(f"Response JSON: {response.json()}")
    assert response.status_code == 400
    detail = response.json().get("detail", [])
    assert isinstance(detail, list)
    assert any("field required" in str(error) for error in detail)

def test_update_product_with_nonexistent_id(mock_db, mock_get_current_user, mocker):
    mocker.patch('jwt.decode', return_value={"user_id": "user_id"})
    
    response = client.put(
        "/api/v1/product/nonexistent_id",
        json={"name": "Product", "price": 10.0, "description": "Description"},
        headers={"Authorization": "Bearer valid_token"}
    )
    
    print(f"Response JSON: {response.json()}")
    assert response.status_code == 404

def test_update_product_with_special_characters(mock_db, mock_get_current_user, mocker):
    mocker.patch('jwt.decode', return_value={"user_id": "user_id"})
    
    mock_product = MagicMock()
    mock_product.id = 'e65c9f26-696a-42df-a4b9-4da214267'
    mock_product.name = 'Special Prod@uct'
    mock_product.price = 100.0
    mock_product.description = 'Special Description'
    mock_product.updated_at = None

    mock_db().query().filter().first.return_value = mock_product

    def mock_commit():
        mock_product.name = 'Updated @Product! #2024'
        mock_product.price = 99.99
        mock_product.description = 'Updated & Description!'
        mock_product.updated_at = datetime.utcnow()

    mock_db().commit = mock_commit

    product_update = {
        "name": "Updated @Product! #2024",
        "price": 99.99,
        "description": "Updated & Description!"
    }
    
    response = client.put(
        "/api/v1/product/e65c9f26-696a-42df-a4b9-4da214267",
        json=product_update,
        headers={"Authorization": "Bearer valid_token"}
    )
    
    print(f"Response JSON: {response.json()}")
    assert response.status_code == 200
    assert response.json()["name"] == "Updated @Product! #2024"
    assert response.json()["price"] == 99.99
    assert response.json()["description"] == "Updated & Description!"
    assert response.json()["updated_at"] is not None
