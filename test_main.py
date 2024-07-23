# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from main_ import app, get_db
import app.models as models
from app.auth import AuthJWT
import os

# Fetch the database URL from the environment variables
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fastuser:password@localhost/hng_fast")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def db_session():
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def test_product(db_session):
    product = models.Product(name="Test Product", price=100.0, description="Test Description")
    db_session.add(product)
    db_session.commit()
    return product

@pytest.fixture(scope="module")
def auth_token():
    auth = AuthJWT()
    return auth.create_access_token(subject="testuser")

def test_get_product_success(client, test_product, auth_token):
    response = client.get(
        f"/api/v1/products/{test_product.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Product details retrieved successfully",
        "status_code": 200,
        "data": {
            "id": test_product.id,
            "name": test_product.name,
            "price": test_product.price,
            "description": test_product.description
        }
    }

def test_get_product_not_found(client, auth_token):
    response = client.get(
        "/api/v1/products/999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }

def test_get_product_unauthorized(client, test_product):
    response = client.get(
        f"/api/v1/products/{test_product.id}",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Unauthorized access"
    }
