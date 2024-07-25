import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from datetime import datetime
from fastapi import HTTPException
from api.v1.schemas.product import ProductUpdate
from api.v1.models.product import Product
from api.v1.models.user import User

client = TestClient(app)

@pytest.fixture
def mock_db(mocker):
    # Mock the database session
    mock_db = mocker.patch('api.db.database.get_db', return_value=MagicMock())
    yield mock_db

def test_update_product_with_valid_token(mock_db, mocker):
    # Mock get_current_user
    mock_get_current_user = mocker.patch('api.utils.dependencies.get_current_user', return_value=User(id='user_id', is_super_admin=False))
    
    # Mock the ProductModel
    mock_product = MagicMock()
    mock_product.id = 'e65c9f26-696a-42df-a4b9-4da21426734c'
    mock_product.name = 'Old Product'
    mock_product.price = 20.0
    mock_product.description = 'Old Description'
    mock_product.updated_at = None
    
    # Mock the query to return the mock_product
    mock_db().query().filter().first.return_value = mock_product
    
    # Mock the commit method
    mock_db().commit = MagicMock()
    
    # Define the payload
    product_update = {
        "name": "Updated Product",
        "price": 25.0,
        "description": "Updated Description"
    }
    
    response = client.put("/product/e65c9f26-696a-42df-a4b9-4da21426734c", json=product_update, headers={"Authorization": "Bearer valid_token"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Product"
    assert response.json()["price"] == 25.0
    assert response.json()["description"] == "Updated Description"


def test_update_product_without_token(mock_db, mocker):
    response = client.put("/product/e65c9f26-696a-42df-a4b9-4da21426734c", json={"name": "Product"})
    assert response.status_code == 401

def test_update_product_with_invalid_token(mock_db, mocker):
    mock_get_current_user = mocker.patch('api.utils.dependencies.get_current_user', side_effect=HTTPException(status_code=401, detail="Invalid credentials"))
    
    response = client.put("/product/e65c9f26-696a-42df-a4b9-4da21426734c", json={"name": "Product"}, headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

def test_update_product_with_missing_fields(mock_db, mocker):
    response = client.put("/product/e65c9f26-696a-42df-a4b9-4da21426734c", json={})
    assert response.status_code == 400
    assert "name" in response.json()["detail"]
    assert "price" in response.json()["detail"]

def test_update_product_with_nonexistent_id(mock_db, mocker):
    mock_db().query().filter().first.return_value = None
    
    response = client.put("/product/e65c9f26-696a-42df-a4b9-4da21426734c", json={"name": "Product", "price": 10.0, "description": "Description"}, headers={"Authorization": "Bearer valid_token"})
    assert response.status_code == 404

def test_update_product_with_special_characters(mock_db, mocker):
    mock_product = MagicMock()
    mock_product.id = 'e65c9f26-696a-42df-a4b9-4da21426734c'
    mock_product.name = 'Special Product'
    mock_product.price = 100.0
    mock_product.description = 'Special Description'
    mock_product.updated_at = None
    
    # Mock the query to return the mock_product
    mock_db().query().filter().first.return_value = mock_product
    
    # Mock the save operation
    def mock_save():
        mock_product.name = 'Updated @Product! #2024'
        mock_product.price = 99.99
        mock_product.description = 'Updated & Description!'
        mock_product.updated_at = datetime.now()
    
    mock_db().commit = mock_save
    
    product_update = {
        "name": "Updated @Product! #2024",
        "price": 99.99,
        "description": "Updated & Description!"
    }
    
    response = client.put("/product/e65c9f26-696a-42df-a4b9-4da21426734c", json=product_update, headers={"Authorization": "Bearer valid_token"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated @Product! #2024"
    assert response.json()["price"] == 99.99
    assert response.json()["description"] == "Updated & Description!"
    