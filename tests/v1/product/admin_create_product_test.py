from fastapi.encoders import jsonable_encoder
from uuid_extensions import uuid7
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.dependencies import get_current_user
from api.v1.models import User, Organization, Product, ProductCategory
from api.v1.schemas.product import ProductCreate
from api.v1.services.user import user_service
from api.v1.services.organization import organization_service
from api.v1.services.product_category import product_category_service
from api.v1.services.product import product_service
from main import app
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import pytest 
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import pytest

prod_id = str(uuid7())
user_id = str(uuid7())
category_id = str(uuid7())
org_id = str(uuid7())

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session():
    db_session = MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session
    return db_session

# Test User
@pytest.fixture
def test_user():
    return User(
        id=user_id,
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
        is_super_admin=True,
    )


@pytest.fixture
def test_organization(test_user):
    organization = Organization(
        id=org_id,
        company_name="testorg",
    )
    organization.users.append(test_user)
    return organization


@pytest.fixture
def test_category():
    return ProductCategory(
        id=category_id,
        name="Category1"
    )

@pytest.fixture
def access_token_user1(test_user):
    return user_service.create_access_token(user_id=test_user.id)

# Test for creating a product
def test_create_product(
    mock_db_session, 
    test_user, 
    test_organization, 
    test_category,
    access_token_user1,
):
    product_data = {
        "name": "Test Product",
        "description": "Test Description",
        "price": 100.0,
        "org_id": test_organization.id,
        "category_id": test_category.id,
        "quantity": 10,
        "image_url": "http://example.com/image.jpg",
        "status": "in_stock",
        "archived": False
    }

    print()

    mock_product = Product(id=prod_id, **product_data)

    with patch.object(organization_service, 'fetch', return_value=test_organization) as mock_org_service, \
         patch.object(product_category_service, 'fetch', return_value=test_category) as mock_cat_service, \
         patch.object(product_service, 'create', return_value=mock_product) as mock_product_service:
        
        headers = {'Authorization': f'Bearer {access_token_user1}'}
        response = client.post('/api/v1/products/admin/', json=product_data, headers=headers)
        
        print("Response JSON:", response.json())
        
        assert response.status_code == 201, f"Unexpected status code: {response.status_code}"
        assert response.json()["data"]["category_id"] == test_category.id
        assert response.json()["data"]["org_id"] == test_organization.id
    

def test_create_product_missing_field(
    mock_db_session, 
    test_user, 
    test_organization, 
    test_category,
    access_token_user1,
):
    product_data = {
        "description": "Test Description",
        "price": 100.0,
        "org_id": test_organization.id,
        "category_id": test_category.id,
        "quantity": 10,
        "image_url": "http://example.com/image.jpg",
        "status": "in_stock",
        "archived": False
    }

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.post('/api/v1/products/admin/', json=product_data, headers=headers)
    
    print("Response JSON:", response.json())

    assert response.status_code == 422, f"Unexpected status code: {response.status_code}"
    assert response.json()["errors"] == [
        {
            "loc": ["body", "name"],
            "msg": "Field required",
            "type": "missing"
        }
    ]