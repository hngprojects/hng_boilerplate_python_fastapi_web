from api.utils.settings import settings
from fastapi.testclient import TestClient
from ..database import get_db, Base
from api.v1.models.product import Product
from api.v1.models.user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from ...main import app
from decouple import config
import bcrypt



DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
DB_TYPE = settings.DB_TYPE

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Acess Get Protected Single Product Endpoint without Authorization
def test_unauth_access_product(db_session, test_client):
    # Add product to db
    product = Product(name="bed", price=400000)
    db_session.add(product)
    db_session.commit()

    productID = product.id # Fetch id and make request using product's id
    response = test_client.get(f"/api/v1/products/{productID}")
    assert response.status_code == 401 # Unauthorized
