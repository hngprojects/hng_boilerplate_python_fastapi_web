"""
Covers Test for:
1. Successfully like a blog post.
2. Like a blog post user have already liked.
3. Like a blog with invalid blog id.
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.v1.models import User, Blog, BlogLike
from api.db.database import get_db
import pytest
from uuid import uuid4
from api.v1.routes.user import get_current_user_details
from main import app

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Mock current user dependency
def override_get_current_user():
    return User(id=uuid4(), username="testuser")


app.dependency_overrides[get_current_user_details] = override_get_current_user


@pytest.fixture(scope="function")
def setup_db():
    db = TestingSessionLocal()
    user = User(id=uuid4(), username="testuser")
    blog = Blog(id=uuid4(), title="Test Blog", content="Test Content", like_count=0)
    db.add(user)
    db.add(blog)
    db.commit()
    yield db
    db.query(User).delete()
    db.query(Blog).delete()
    db.query(BlogLike).delete()
    db.commit()
    db.close()


def test_like_blog_success(setup_db):
    db = setup_db
    blog = db.query(Blog).first()
    response = client.post(f"/blogs/{blog.id}/like")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "message": "Like recorded successfully."}


def test_like_blog_already_liked(setup_db):
    db = setup_db
    blog = db.query(Blog).first()
    user = db.query(User).first()
    blog_like = BlogLike(blog_id=str(blog.id), user_id=str(user.id), ip_address="127.0.0.1")
    db.add(blog_like)
    db.commit()
    response = client.post(f"/blogs/{blog.id}/like")
    assert response.status_code == 403
    assert response.json() == {"status_code": 403, "message": "You have already liked this blog post."}


def test_like_blog_invalid_blog_id(setup_db):
    invalid_blog_id = uuid4()
    response = client.post(f"/blogs/{invalid_blog_id}/like")
    assert response.status_code == 404
    assert response.json() == {"status_code": 404, "message": "Blog post not found."}
