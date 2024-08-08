from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.organization import Organization
from api.v1.models.product import ProductCategory
from api.v1.services.product import ProductCategoryService
from api.v1.services.organization import organization_service
from api.v1.services.user import user_service
from api.v1.models.user import User
from main import app



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


def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="test@gmail.com",
        password=user_service.hash_password("Testuser@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_product_category():
    return ProductCategory(
        id=str(uuid7()),
        name="Test Category",
    )

def mock_org():
    return Organization(
        id=str(uuid7()),
        name="Test Organization",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )



def test_create_category_success(client, db_session_mock):
    '''Test to successfully create a new product category'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user
    app.dependency_overrides[organization_service.create] = lambda: mock_org

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None


    mock_category_instance = mock_product_category()
    mock_org_instance = mock_org()
    mock_user_instance = mock_get_current_user()

    mock_org_instance.users.append(mock_user_instance)


    with patch("api.v1.services.product.ProductCategoryService.create", return_value=mock_category_instance) as mock_create:

        response = client.post(f'/api/v1/products/categories/{mock_org_instance.id}', json={
            "name": "Test Category"
        })

        assert response.status_code == 201


def test_create_category_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''    


    mock_category_instance = mock_product_category()
    mock_org_instance = mock_org()
    mock_user_instance = mock_get_current_user()

    mock_org_instance.users.append(mock_user_instance)


    with patch("api.v1.services.product.ProductCategoryService.create", return_value=mock_category_instance) as mock_create:

        response = client.post(f'/api/v1/products/categories/{mock_org_instance.id}', json={
            "name": "Test Category"
        })

        assert response.status_code == 401
