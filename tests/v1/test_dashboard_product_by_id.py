import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from fastapi import status

from main import app
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.product import product_service
from api.v1.schemas.product import DashboardProductData

client = TestClient(app)

# Mock dependencies
class MockSession(Session):
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

def override_get_db():
    yield Session()

def override_get_current_super_admin():
    class User:
        is_super_admin = True
    return User()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[user_service.get_current_super_admin] = override_get_current_super_admin

@pytest.fixture
def product_data():
    return DashboardProductData(
        id="1",
        name="Test Product",
        description="This is a test product",
        price=10.0,
        org_id="1"
    )

def test_dashboard_get_product_not_super_admin(monkeypatch):
    def mock_get_current_super_admin():
        class User:
            is_super_admin = False
        return User()
    
    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_super_admin

    response = client.get("/api/v1/dashboard/products/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    print(response.json())
    assert response.json().get("message") == "You are NOT authorized to access this endpoint"

def test_dashboard_get_product_not_found(monkeypatch):
    def mock_get_current_super_admin():
        class User:
            is_super_admin = True
        return User()

    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_super_admin

    def mock_fetch(db, product_id):
        return None

    monkeypatch.setattr(product_service, "fetch", mock_fetch)

    response = client.get("/api/v1/dashboard/products/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    print(response.json())
    assert response.json().get("message") == "Product with id 1 not found"

def test_dashboard_get_product_success(monkeypatch, product_data):
    def mock_get_current_super_admin():
        class User:
            is_super_admin = True
        return User()

    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_super_admin

    def mock_fetch(db, product_id):
        return product_data

    monkeypatch.setattr(product_service, "fetch", mock_fetch)

    response = client.get("/api/v1/dashboard/products/1")
    assert response.status_code == status.HTTP_200_OK
    print(response.json())
    assert response.json() == {
        "status_code": status.HTTP_200_OK,
        "message": "Product retrieved successfully",
        "data": {
            "id": product_data.id,
            "name": product_data.name,
            "description": product_data.description,
            "price": product_data.price,
            "org_id": product_data.org_id,
        }
    }