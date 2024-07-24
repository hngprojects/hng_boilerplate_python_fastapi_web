from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.dependencies import get_super_admin
from api.v1.models.blog import Blog
from api.v1.schemas.user import User
from main import app  # assuming your FastAPI app is in main.py


# Mock dependencies
def mock_get_db():
    # This should return a mock database session
    return Session()

def mock_get_super_admin():
    # This should return a mock super admin user
    return User(id="1", is_superadmin=True)

app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_super_admin] = mock_get_super_admin

client = TestClient(app)

def test_delete_blog_success():
    # Arrange
    blog_id = "test_id"
    mock_blog = Blog(id=blog_id, title="Test Blog", content="Test Content", is_deleted=False)
    
    with patch('api.v1.models.blog.Blog.query') as mock_query:
        mock_query.filter.return_value.first.return_value = mock_blog
        
        # Act
        response = client.delete(f"/api/v1/blog/{blog_id}")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": "Blog post deleted successfully", "status_code": 202}
        assert mock_blog.is_deleted == True

def test_delete_blog_unauthorized():
    blog_id = "test_id"
    app.dependency_overrides[get_super_admin] = lambda: None
    
    response = client.delete(f"/api/v1/blog/{blog_id}")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized User"

def test_delete_blog_not_found():
    # Arrange
    blog_id = "non_existent_id"
    
    with patch('api.v1.models.blog.Blog.query') as mock_query:
        mock_query.filter.return_value.first.return_value = None
        
        # Act
        response = client.delete(f"/api/v1/blog/{blog_id}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Blog with the given ID does not exist"

def test_get_all_blogs():
    # Arrange
    mock_blogs = [
        Blog(id="1", title="Blog 1", content="Content 1", is_deleted=False),
        Blog(id="2", title="Blog 2", content="Content 2", is_deleted=False)
    ]
    
    with patch('api.v1.models.blog.Blog.query') as mock_query:
        mock_query.filter.return_value.all.return_value = mock_blogs
        
        # Act
        response = client.get("/blog/")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["title"] == "Blog 1"
        assert response.json()[1]["title"] == "Blog 2"
