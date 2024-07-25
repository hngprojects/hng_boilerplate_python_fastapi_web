from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.utils.dependencies import get_super_admin
from api.v1.models import User
from api.v1.models.blog import Blog
from main import app


def mock_get_db():
    db_session = MagicMock()
    yield db_session


def mock_get_super_admin():
    return User(id="1", is_super_admin=True)

@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    

app.dependency_overrides[get_super_admin] = mock_get_super_admin



def test_delete_blog_success(client, db_session_mock):
    blog_id = uuid7()
    mock_blog = Blog(id=blog_id, title="Test Blog",
                     content="Test Content", is_deleted=False)

    db_session_mock.query(Blog).filter(blog_id).first.return_value.id = [mock_blog]

    response = client.delete(f"/api/v1/blogs/{mock_blog.id}")

        
    assert response.status_code == 200
    assert response.json() == {
        "message": "Blog post deleted successfully", "status_code": 200}


def test_delete_blog_unauthorized(client, db_session_mock):
    blog_id = uuid7()
    mock_blog = Blog(id=blog_id, title="Test Blog",
                     content="Test Content", is_deleted=False)
    app.dependency_overrides[get_super_admin] = lambda: None

    response = client.delete(f"/api/v1/blogs/{mock_blog.id}")


    assert response.status_code == 200
    assert response.json()["message"] == "Unauthorized User"


# def test_delete_blog_not_found(client, db_session_mock):
#     blog_id = "non_existent_id"
#     app.dependency_overrides[get_super_admin] = mock_get_super_admin

#     db_session_mock.query().filter.first.return_value =  None

#     response = client.delete(f"/api/v1/blog/{blog_id}")

#     assert response.status_code == 200
#     assert response.json()["message"] == "Blog with the given ID does not exist"


if __name__ == "__main__":
    pytest.main()
