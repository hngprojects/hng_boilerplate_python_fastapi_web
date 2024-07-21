import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from api.db.database import get_db
from api.v1.models.product import Product
from api.v1.models.user import User
from api.utils.auth import create_access_token

client = TestClient(app)

@pytest.fixture
def db_session_mock(mocker):
    db_session = mocker.MagicMock()
    yield db_session

@pytest.fixture(autouse=True)
def override_get_db(mocker, db_session_mock):
    mocker.patch("app.api.v1.routes.product.get_db", return_value=db_session_mock)

@pytest.fixture
def admin_user():
    return User(id="12345678-1234-1234-1234-123456789012", username="admin", email="admin@example.com", is_admin=True)

@pytest.fixture
def non_admin_user():
    return User(id="12345678-1234-1234-1234-123456789013", username="nonadmin", email="nonadmin@example.com", is_admin=False)

@pytest.fixture
def product():
    return Product(id="12345678-1234-1234-1234-123456789014", name="Test Product", description="Description", price=10.0)

def test_delete_product_success(db_session_mock, admin_user, product):
    
    db_session_mock.query(Product).filter().first.return_value = product
    db_session_mock.delete.return_value = None
    db_session_mock.commit.return_value = None

    token = create_access_token(data={"username": admin_user.username})


    response = client.delete(f"/api/v1/products/{product.id}", headers={"Authorization": f"Bearer {token}"})


    assert response.status_code == 204
    assert response.json() == {
        "status": "success",
        "message": "Product deleted successfully"
    }


def test_delete_nonexistent_product(db_session_mock, admin_user):
 
    db_session_mock.query(Product).filter().first.return_value = None

    token = create_access_token(data={"username": admin_user.username})


    response = client.delete("/api/v1/products/12345678-1234-1234-1234-123456789999", headers={"Authorization": f"Bearer {token}"})

    
    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}

def test_delete_product_unauthorized(db_session_mock, product):
    
    db_session_mock.query(Product).filter().first.return_value = product

    
    response = client.delete(f"/api/v1/products/{product.id}")

    
    assert response.status_code == 401

def test_delete_product_forbidden(db_session_mock, non_admin_user, product):
    
    db_session_mock.query(Product).filter().first.return_value = product

    token = create_access_token(data={"username": non_admin_user.username})

    
    response = client.delete(f"/api/v1/products/{product.id}", headers={"Authorization": f"Bearer {token}"})

    
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have permission to delete this product"}

if __name__ == "__main__":
    pytest.main()
