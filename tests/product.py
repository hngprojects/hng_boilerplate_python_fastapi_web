from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ..main import app
from decouple import config


from api.db.database import get_db, Base
from api.v1.models.user import User
from api.v1.models.organization import Organization
from api.v1.models.product import Product


# Create a test database URL
DB_TYPE = config("DB_TYPE")
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
MYSQL_DRIVER = config("MYSQL_DRIVER")
DATABASE_URL = ""

SQLALCHEMY_DATABASE_URL = f'{DB_TYPE}+{MYSQL_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'


# Create a new database session for testing
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)


@pytest.fixture(scope="module")
# def setup_database():
#     Base.metadata.create_all(bind=engine)
#     db = TestingSessionLocal()
#     # Create test data
#     user = User(username="testuser",
#                 email="testuser@example.com", password="&Passw1rd")
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     organization = Organization(name="Test Organization")
#     db.add(organization)
#     db.commit()
#     db.refresh(organization)
#     product = Product(name="Test Product",
#                       description="A test product", price=10.99)
#     db.add(product)
#     db.commit()
#     db.refresh(product)
#     db.execute("INSERT INTO user_organization_association (user_id, organization_id) VALUES (:user_id, :org_id)", {
#                "user_id": user.id, "org_id": organization.id})
#     db.commit()
#     yield db
#     db.close()
#     Base.metadata.drop_all(bind=engine)
def test_get_product_success(setup_database):
    response = client.post(
        "/api/v1/products",
        json={"org_id": 1, "pro_id": 1},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "message": "Product Test Product retrieved successfully",
        "data": {
            "id": 1,
            "name": "Test Product",
            "description": "A test product",
            "price": 10.99
        }
    }


def test_get_product_org_not_found(setup_database):
    response = client.post(
        "/api/v1/products",
        json={"org_id": 999, "pro_id": 1},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Organization not found"}


def test_get_product_not_found(setup_database):
    response = client.post(
        "/api/v1/products",
        json={"org_id": 1, "pro_id": 999},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_get_product_unauthorized(setup_database):
    response = client.post(
        "/api/v1/products",
        json={"org_id": 1, "pro_id": 1}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
