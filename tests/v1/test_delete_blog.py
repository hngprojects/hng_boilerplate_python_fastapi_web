import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.models.blog import Blog
from unittest.mock import MagicMock
import uuid
from api.db.database import get_db
from api.utils.dependencies import get_current_admin

client = TestClient(app)

# Mock the database dependency
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    app.dependency_overrides[get_db] = get_db_override

# Mock the get_current_admin dependency
@pytest.fixture(autouse=True)
def override_get_current_admin():
    app.dependency_overrides[get_current_admin] = lambda: {"username": "admin"}
    
def create_blog(db_session_mock, id: str, is_deleted: bool):
    blog = Blog(id=id, title="Test Blog", content="Content", image_url="http://example.com/image.jpg",
                tags=["test"], excerpt="Excerpt", is_deleted=is_deleted)
    db_session_mock.query.return_value.filter_by.return_value.first.return_value = blog

def test_delete_blog_valid_uuid(db_session_mock):
    blog_id = str(uuid.uuid4())
    create_blog(db_session_mock, blog_id, False)
    db_session_mock.query.return_value.filter.return_value.first.return_value = db_session_mock.query.return_value.filter_by.return_value.first.return_value
    response = client.delete(f"/api/v1/blogs/{blog_id}")
    assert response.status_code == 202
    assert response.json() == {
        "message": "Blog successfully deleted", "status_code": 202}

def test_delete_blog_already_deleted(db_session_mock):
    blog_id = str(uuid.uuid4())
    create_blog(db_session_mock, blog_id, True)
    response = client.delete(f"/api/v1/blogs/{blog_id}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Blog not active"}

def test_delete_blog_not_exist(db_session_mock):
    invalid_id = "str(uuid.uuid4())"
    response = client.delete(f"/api/v1/blogs/{invalid_id}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Id"}

def test_delete_blog_invalid_uuid():
    invalid_id = "invalid-uuid"
    response = client.delete(f"/api/v1/blogs/{invalid_id}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Id"}
