import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from ....main import app
from api.v1.routes.blog import get_db

from api.v1.services.user import user_service
from api.v1.models.user import User
from api.v1.models.product import Product


# Mock database dependency
@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session


@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


# Mock user service dependency

user_id = uuid7()
product_id = uuid7()
org_id = uuid7()
timezone_offset = -8.0
tzinfo = timezone(timedelta(hours=timezone_offset))
timeinfo = datetime.now(tzinfo)
created_at = timeinfo
updated_at = timeinfo
access_token = user_service.create_access_token(str(user_id))

# Create test user

user = User(
    id=user_id,
    username="testuser1",
    email="testuser1@gmail.com",
    password=user_service.hash_password("Testpassword@123"),
    first_name="Test",
    last_name="User",
    is_active=False,
    created_at=created_at,
    updated_at=updated_at,
)

# create test product

product = Product(
    id=product_id,
    name="Test Product",
    description="This is my test product",
    price=9.99,
    org_id=org_id,
    created_at=created_at,
    updated_at=updated_at,
)


def test_get_single_product_success(client, db_session_mock):
    db_session_mock.query().filter().first.return_value = product

    headers = {"authorization": f"Bearer {access_token}"}

    response = client.get("api/v1/dashboard/products/{product_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["success"] == True


def test_get_single_product_unauthenticated_user(client, db_session_mock):
    db_session_mock.query().filter().first.return_value = product

    response = client.get("api/v1/dashboard/products/{product_id}")

    assert response.status_code == 401
    assert response.json()["success"] == False
