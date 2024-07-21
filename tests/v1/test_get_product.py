from api.utils.settings import settings
from fastapi.testclient import TestClient
from ..database import get_db, Base
from api.v1.models.product import Product
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from ...main import app
from decouple import config



DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
DB_TYPE = settings.DB_TYPE

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# engine = create_engine(
#     DATABASE_URL,
#     # connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )

# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.create_all(bind=engine)

# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()


# app.dependency_overrides[get_db] = override_get_db
# client = TestClient(app)

# db = next(override_get_db())

# def test_unauth_access_product(test_client):
    # product = db.query(Product).first()
    # productID = product.id
    # response = test_client.get(f"/api/v1/products/{productID}")
    # assert response.status_code == 401 # Unauthorized

def test_auth_access_product(test_client):
    response = test_client.post("/api/v1/auth/register", json = {
        "username": "johndoe",
        "password": "securepassword123",
        "first_name": "John",
        "last_name": "Doe",
        "email": "test@example.com"
    })
    assert response.status_code == 201
    
    response = test_client.post("/api/v1/auth/login", json = {
        "username": "johndoe",
        "password": "securepassword123"
    })
    assert response.status_code == 200
    data = response.json()
    token = data['access_token']
    assert token is not None or token != ""


    product = db.query(Product).first()
    productID = product.id
    response = client.get(f"/api/v1/products/{productID}", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200 # Success

