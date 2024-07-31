import os
import pytest
import jwt
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from main import app
from api.db.database import SessionLocal
from api.v1.models.comment import Comment
from api.v1.models.user import User
from api.v1.models.blog import Blog

# Load environment variables from .env file
load_dotenv()

# Secret key for JWT encoding/decoding
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def create_test_blog(db_session):
    blog = Blog(id="test_blog_id", author_id="test_user_id", title="Test Blog", content="Blog content")
    db_session.add(blog)
    db_session.commit()
    return blog

@pytest.fixture
def create_test_comment(db_session, create_test_blog):
    comment = Comment(id="test_comment_id", user_id="test_user_id", blog_id=create_test_blog.id, content="Original content", created_at=datetime.utcnow())
    db_session.add(comment)
    db_session.commit()
    return comment

@pytest.fixture
def create_test_user(db_session):
    user = User(id="test_user_id", email="testuser@example.com", password="fakehashedpassword", first_name="Test", last_name="User")
    db_session.add(user)
    db_session.commit()
    return user

def generate_token(user_id):
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def test_update_comment_success(client, create_test_comment, create_test_user):
    update_data = {"content": "Updated comment content."}
    token = generate_token(create_test_user.id)
    response = client.patch(
        f"/comments/{create_test_comment.id}/",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["content"] == "Updated comment content."
    assert response_data["id"] == create_test_comment.id

def test_update_comment_not_found(client, create_test_user):
    update_data = {"content": "Updated comment content."}
    token = generate_token(create_test_user.id)
    response = client.patch(
        "/comments/non_existent_comment_id/",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Comment not found"

def test_update_comment_unauthorized(client, create_test_comment, db_session):
    another_user = User(id="another_user_id", email="anotheruser@example.com", password="fakehashedpassword", first_name="Another", last_name="User")
    db_session.add(another_user)
    db_session.commit()
    token = generate_token(another_user.id)
    response = client.patch(
        f"/comments/{create_test_comment.id}/",
        json={"content": "Unauthorized update attempt."},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "You do not have permission to update this comment."

