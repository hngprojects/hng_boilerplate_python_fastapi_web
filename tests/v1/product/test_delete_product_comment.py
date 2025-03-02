import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from uuid_extensions import uuid7
from uuid import uuid4


from main import app
from sqlalchemy.orm import Session
from api.v1.services.product_comment import product_comment_service
from api.v1.models import User
from api.utils.dependencies import get_current_user
from api.v1.services.product_comment import ProductCommentService
from api.utils.success_response import success_response


from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session


from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.v1.models.product import Product, ProductComment
from api.v1.services.product_comment import product_comment_service
from api.v1.services.product import product_service
from main import app
from faker import Faker

fake = Faker()

def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_product():
    return Product(
        id=str(uuid7()),
        name=fake.numerify(text='Intel Core i%-%%##K vs AMD Ryzen % %%##X'),
        description=fake.paragraph(),
        price=fake.pydecimal(left_digits=3, right_digits=2, positive=True),
        org_id=str(uuid7()),
        category_id=str(uuid7()),
        quantity=fake.random_int(min=0, max=100),
        image_url=fake.image_url(),
        status=fake.random_element(elements=("in_stock", "out_of_stock", "low_on_stock")),
        archived=fake.boolean(),
        filter_status=fake.random_element(elements=("active", "draft")),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

# def mock_product_comment():
#     return ProductComment(
#         id=str(uuid7()),
#         content=fake.paragraph(),
#         created_at=datetime.now(timezone.utc),
#         updated_at=datetime.now(timezone.utc)
#     )

def mock_product_comment():
    return ProductComment(
        id=str(uuid7()),
        product_id=uuid4(),  # Now a UUID object, not a string
        content=fake.paragraph(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


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




# Add these after your existing tests

def test_delete_product_comment_success(client, db_session_mock):
    """Test successful deletion of a comment by owner"""
    # Mock user and data
    mock_user = mock_get_current_admin()
    mock_comment = mock_product_comment()
    mock_comment.user_id = mock_user.id  # Match ownership
    mock_product_instance = mock_product()
    mock_comment.product_id = mock_product_instance.id  # Match product ID

    # Mock dependencies
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    # Patch service methods
    with patch.object(ProductCommentService, 'fetch', return_value=mock_comment), \
         patch.object(Session, 'delete') as mock_delete, \
         patch.object(Session, 'commit') as mock_commit:
        
        response = client.delete(
            f"/api/v1/products/{mock_product_instance.id}/comments/{mock_comment.id}",
            headers={'Authorization': 'Bearer token'}
        )

        # Assertions
        assert response.status_code == 200
       

def test_delete_comment_unauthorized(client, db_session_mock):
    """Test deletion by non-owner"""
    mock_user = mock_get_current_admin()
    mock_comment = mock_product_comment()
    mock_comment.user_id = "different-user-id"  # Non-owner
    mock_product_instance = mock_product()

    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    with patch.object(ProductCommentService, 'fetch', return_value=mock_comment):
        response = client.delete(
            f"/api/v1/products/{mock_product_instance.id}/comments/{mock_comment.id}",
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 401
       

def test_delete_comment_not_found(client, db_session_mock):
    """Test deletion of non-existent comment"""
    mock_user = mock_get_current_admin()
    mock_product_instance = mock_product()
    fake_comment_id = str(uuid7())  # Random ID

    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    with patch.object(ProductCommentService, 'fetch', side_effect=HTTPException(404)):
        response = client.delete(
            f"/api/v1/products/{mock_product_instance.id}/comments/{fake_comment_id}",
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 404
        

def test_delete_comment_product_mismatch(client, db_session_mock):
    """Test comment doesn't belong to specified product"""
    mock_user = mock_get_current_admin()
   
    comment_product_id = uuid4()  
    fake_product_id = uuid4()      
    
    
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    with patch.object(ProductCommentService, 'fetch', return_value=""):
        response = client.delete(
            
            f"/api/v1/products/{str(fake_product_id)}/comments/{comment_product_id}",
            headers={'Authorization': 'Bearer token'}
        )
    
        assert response.status_code == 404
        