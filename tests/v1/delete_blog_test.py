from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.db.database import get_db
from api.utils.dependencies import get_super_admin
from api.v1.models import User
from api.v1.models.blog import Blog
from main import app


@pytest.fixture
def mock_get_db():
    db_session = MagicMock()
    yield db_session

@pytest.fixture
def mock_get_super_admin():
    return User(id="1", is_superadmin=True)

app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_super_admin] = mock_get_super_admin

client = TestClient(app)

def test_delete_blog_success():
    blog_id = "1"
    mock_blog = Blog(id=blog_id, title="Test Blog", content="Test Content", is_deleted=False)
    
    with patch('api.v1.models.blog.Blog') as mock_query:
        mock_query.filter.return_value.first.return_value = mock_blog
        
        response = client.delete(f"/api/v1/blog/{blog_id}")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Blog post deleted successfully", "status_code": 200}
        assert mock_blog.is_deleted == True

def test_delete_blog_unauthorized():
    blog_id = "1"
    mock_blog = Blog(id=blog_id, title="Test Blog", content="Test Content", is_deleted=False)
    app.dependency_overrides[get_super_admin] = lambda: None
    
    response = client.delete(f"/api/v1/blog/{blog_id}")
    
    assert response.status_code == 403
    assert response.json()["message"] == "Unauthorized User"

def test_delete_blog_not_found():
    blog_id = "non_existent_id"
    
    with patch('api.v1.models.blog.Blog') as mock_query:
        mock_query.filter.return_value.first.return_value = None
        
        response = client.delete(f"/api/v1/blog/{blog_id}")
        
        assert response.status_code == 404
        assert response.json()["message"] == "Blog with the given ID does not exist"


if __name__ == "__main__":
    pytest.main()
