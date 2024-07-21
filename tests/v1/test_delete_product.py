# tests/test_delete_product.py

import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from api.v1.models.user import User
from api.v1.models.product import Product
from api.utils.auth import hash_password, create_access_token

DATABASE_URL = "sqlite:///./test.db"  # Use a test database

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()

def create_test_user(db):
    password = hash_password("password")
    user = User(username="testuser", email="testuser@example.com", password=password, is_admin=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_test_product(db, user_id):
    product = Product(name="Test Product", description="Description", price=10.0)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def test_delete_product_success(db):
    user = create_test_user(db)
    product = create_test_product(db, user.id)
    token = create_access_token(data={"username": user.username})

    response = client.delete(f"/api/v1/products/{product.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

def test_delete_nonexistent_product(db):
    user = create_test_user(db)
    token = create_access_token(data={"username": user.username})

    response = client.delete("/api/v1/products/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}

def test_delete_product_unauthorized(db):
    user = create_test_user(db)
    product = create_test_product(db, user.id)

    response = client.delete(f"/api/v1/products/{product.id}")
    assert response.status_code == 401

def test_delete_product_forbidden(db):
    user = create_test_user(db)
    user.is_admin = False
    db.commit()
    token = create_access_token(data={"username": user.username})

    response = client.delete(f"/api/v1/products/{product.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have permission to delete this product"}
