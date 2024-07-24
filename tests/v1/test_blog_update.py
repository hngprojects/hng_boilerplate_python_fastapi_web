import pytest
from fastapi.testclient import TestClient
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
import sys
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from main import app
from api.utils.dependencies import get_db, get_current_user
from api.v1.models.user import User
from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogRequest
from fastapi.encoders import jsonable_encoder

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_db_session():
    db = MagicMock(spec=Session)
    yield db

@pytest.fixture
def current_user():
    return User(id=f'{uuid7()}', username="testuser", email="test@example.com", password="hashedpassword1", first_name="test", last_name="user")

@pytest.fixture
def valid_blog_post():
    return BlogRequest(title="Updated Title", content="Updated Content")

@pytest.fixture
def existing_blog_post(mock_db_session, current_user):
    blog = Blog(id=f'{uuid7()}', title="Original Title", content="Original Content", author_id=current_user.id)
    mock_db_session.query(Blog).filter(Blog.id == blog.id).first.return_value = blog
    return blog

@pytest.mark.asyncio
async def test_update_blog_success(client, mock_db_session, current_user, valid_blog_post, existing_blog_post):
    # Mock the dependencies
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: current_user

    response = client.put(f"api/v1/blogs/{existing_blog_post.id}", json=valid_blog_post.model_dump())

    assert response.status_code == 200
    assert response.json() == {
        "status": "200",
        "message": "Blog post updated successfully",
        "data": {"post": jsonable_encoder(existing_blog_post)}
    }
    assert existing_blog_post.title == valid_blog_post.title
    assert existing_blog_post.content == valid_blog_post.content

@pytest.mark.asyncio
async def test_update_blog_not_found(client, mock_db_session, current_user, valid_blog_post):
    mock_db_session.query(Blog).filter(Blog.id == f'{uuid7()}').first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: current_user

    response = client.put(f"api/v1/blogs/{uuid7()}", json=valid_blog_post.model_dump())

    assert response.status_code == 404
    assert response.json() == {'message': 'Post not Found', 'status_code': 404, 'success': False}

@pytest.mark.asyncio
async def test_update_blog_forbidden(client, mock_db_session, current_user, valid_blog_post, existing_blog_post):
    # Simulate a different user
    different_user = User(id=f'{uuid7()}', username="otheruser", email="other@example.com", password="hashedpassword1", first_name="other", last_name="user")

    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: different_user

    response = client.put(f"api/v1/blogs/{existing_blog_post.id}", json=valid_blog_post.model_dump())

    assert response.status_code == 403
    assert response.json() == {'message': 'Not authorized to update this blog', 'status_code': 403, 'success': False}

@pytest.mark.asyncio
async def test_update_blog_empty_fields(client, mock_db_session, current_user, existing_blog_post):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: current_user

    response = client.put(f"api/v1/blogs/{existing_blog_post.id}", json={"title": "", "content": ""})

    assert response.status_code == 400
    assert response.json() == {'message': 'Title and content cannot be empty', 'status_code': 400, 'success': False}

@pytest.mark.asyncio
async def test_update_blog_internal_error(client, mock_db_session, current_user, valid_blog_post, existing_blog_post):
    # Simulate a database error
    mock_db_session.commit.side_effect = Exception("Database error")

    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: current_user

    response = client.put(f"api/v1/blogs/{existing_blog_post.id}", json=valid_blog_post.model_dump())

    assert response.status_code == 500
    assert response.json() == {'message': 'An error occurred while updating the blog post', 'status_code': 500, 'success': False}
