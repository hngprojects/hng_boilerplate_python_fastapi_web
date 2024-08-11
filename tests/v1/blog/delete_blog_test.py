from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.blog import Blog
from main import app


def mock_get_db():
    db_session = MagicMock()
    yield db_session


def mock_get_current_super_admin():
    return User(id="1", is_superadmin=True)

@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    

def test_delete_blog_success(client, db_session_mock):
    '''Test for success in blog deletion'''

    app.dependency_overrides[get_db] = lambda: db_session_mock
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_super_admin
    blog_id = uuid7()
    mock_blog = Blog(id=blog_id, title="Test Blog",
                     content="Test Content", is_deleted=False)

    db_session_mock.query(Blog).filter(id==blog_id).first.return_value.id = [mock_blog]

    response = client.delete(f"/api/v1/blogs/{mock_blog.id}", headers={'Authorization': 'Bearer token'})

    assert response.status_code == 204

    
def test_delete_blog_not_found(client, db_session_mock):
    '''test for blog not found'''

    db_session_mock.query(Blog).filter(Blog.id == f'{uuid7()}').first.return_value = None

    app.dependency_overrides[get_db] = lambda: db_session_mock
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_super_admin

    response = client.delete(f"api/v1/blogs/{uuid7()}", headers={'Authorization': 'Bearer token'})

    assert response.json()["status_code"] == 404
    assert response.json()["message"] == "Post not found"
    

if __name__ == "__main__":
    pytest.main()
