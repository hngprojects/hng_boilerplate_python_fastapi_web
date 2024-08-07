# Dependencies:
# pip install pytest-mock
import pytest
from api.v1.routes.product import retrieve_categories
from api.v1.services.product import ProductCategoryService
from api.v1.schemas.product import ProductCategoryRetrieve
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.services.user import user_service
from main import app
from unittest.mock import MagicMock



CATEGORY_ENDPOINT = "/api/v1/products/categories"
client = TestClient(app)

def mock_deps():
    return MagicMock(id="user_id")


class TestCodeUnderTest:

    
    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_user] = mock_deps


    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}


    # Retrieve all product categories successfully
    def test_retrieve_all_product_categories_successfully(self, mocker):

        mock_db = mocker.Mock(spec=Session)
        mock_categories = [
            ProductCategoryRetrieve(name="Category 1", id="1"),
            ProductCategoryRetrieve(name="Category 2", id="2")
        ]
        mocker.patch.object(ProductCategoryService, 'fetch_all', return_value=mock_categories)

        response = client.get(CATEGORY_ENDPOINT)

        assert response.status_code == 200
        assert response.json()['data'] == [
            {
            "name":"Category 1",
            "id": "1"
        },
        {
            "name":"Category 2",
            "id": "2"
        },
        
        ]


    # Test unauthenticated user
    def test_retrieve_all_product_categories_unauth(self, mocker):
        app.dependency_overrides = {}
        
        mock_db = mocker.Mock(spec=Session)
        mock_categories = [
            ProductCategoryRetrieve(name="Category 1", id="1"),
            ProductCategoryRetrieve(name="Category 2", id="2")
        ]
        mocker.patch.object(ProductCategoryService, 'fetch_all', return_value=mock_categories)

        response = client.get(CATEGORY_ENDPOINT)

        assert response.status_code == 401