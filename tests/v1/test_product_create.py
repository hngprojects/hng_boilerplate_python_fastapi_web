import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from api.v1.models.product import Product
from api.v1.schemas.product_create import ProductCreate
from api.v1.models.user import User
from api.utils.auth import hash_password
from ...main import app

# Define the database URL
test_db_name = 'testdb'
test_db_pw = 'test'
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:{test_db_pw}@localhost:5432/{test_db_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Create tables in the test database
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def setup_test_user(client):
    db = TestingSessionLocal()
    # Create a test user for authentication
    test_user = User(
        username="testuser1",
        email="testuser1@example.com",
        password=hash_password("testpassword"),
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db.add(test_user)
    db.commit()
    db.close()


def test_create_product_success(client, setup_test_user):
    # Log in to get a token
    response = client.post("/api/v1/auth/login", json={
        "username": "testuser1",
        "password": "testpassword"
    })
    assert response.status_code == 200
    token = response.json().get("access_token")

    # Create a product
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "New Product",
            "description": "A description of the new product.",
            "price": 29.99,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "New Product"
    assert data["price"] == 29.99


def test_create_product_invalid_data(client):
    response = client.post("/api/v1/products/", json={
        "name": "",  # Invalid name
        "description": "No name provided",
        "price": -10  # Invalid price
    })
    assert response.status_code == 401

def test_create_product_unauthorized(client):
    response = client.post("/api/v1/products/", json={
        "name": "Unauthorized Product",
        "description": "This should fail",
        "price": 19.99,
    })
    assert response.status_code == 401

