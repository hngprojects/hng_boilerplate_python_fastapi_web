from datetime import datetime
from unittest.mock import MagicMock
from fastapi import HTTPException
from jose import JWTError
import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.models.user import User
from api.v1.models.product import Product
from api.db.database import get_db
from api.v1.services.user import user_service
from uuid_extensions import uuid7

client = TestClient(app)
user_id = str(uuid7())

class MockSession:
    def query(self, model):
        class MockQuery:
            def filter(self, condition):
                return self

            def all(self):
                return []

            def first(self):
                return None
        
        return MockQuery()

app.dependency_overrides[get_db] = lambda: MockSession()

@pytest.mark.asyncio
async def test_get_products_by_status():
    access_token = user_service.create_access_token(str(user_id))
    response = client.get(
        '/api/v1/products/status?status=in_stock',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    assert response.status_code == 200
    response = response.json()
    assert response["message"] == "Products retrieved successfully"

@pytest.mark.asyncio
async def test_get_products_by_invalid_status():
    access_token = user_service.create_access_token(str(user_id))
    response = client.get(
        '/api/v1/products/status?status=invalid_status', 
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    assert response.status_code == 500
