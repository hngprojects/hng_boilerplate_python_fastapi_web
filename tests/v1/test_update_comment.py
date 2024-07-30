import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from api.db.database import get_db, SessionLocal
from api.v1.models.comment import Comment
from api.v1.models.user import User
from api.v1.models.blog import Blog
import uuid
import jwt

client = TestClient(app)

# Dependency override to use a test database session
def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def create_test_user(db_session):
    user = User(
        id=str(uuid.uuid4()),  # Ensure unique ID
        email=f"testuser{uuid.uuid4()}@example.com",  # Unique email
        password="fakehashedpassword",
        first_name="Test",
        last_name="User"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(scope="function")
def create_test_blog(db_session, create_test_user):
    blog = Blog(
        id=str(uuid.uuid4()),  # Ensure unique ID
        title="Test Blog",
        content="This is a test blog.",
        author_id=create_test_user.id
    )
    db_session.add(blog)
    db_session.commit()
    return blog

@pytest.fixture(scope="function")
def create_test_comment(db_session, create_test_user, create_test_blog):
    comment = Comment(
        id=str(uuid.uuid4()),  # Ensure unique ID
        content="This is a test comment.",
        user_id=create_test_user.id,
        blog_id=create_test_blog.id
    )
    db_session.add(comment)
    db_session.commit()
    return comment

def generate_token(user_id: str):
    secret_key = "your_secret_key"  # Replace with your actual secret key
    algorithm = "HS256"
    token = jwt.encode({"user_id": user_id}, secret_key, algorithm=algorithm)
    return token

def test_update_comment_success(db_session, create_test_user, create_test_comment):
    update_data = {"content": "Updated comment content."}
    token = generate_token(create_test_user.id)
    response = client.put(
        f"/comments/{create_test_comment.id}/",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Comment updated successfully."
    assert response_data["data"]["content"] == "Updated comment content."

def test_update_comment_not_found(db_session, create_test_user):
    update_data = {"content": "Updated comment content."}
    token = generate_token(create_test_user.id)
    response = client.put(
        "/comments/non_existent_comment_id/",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Comment not found."

def test_update_comment_unauthorized(db_session, create_test_user, create_test_comment):
    update_data = {"content": "Updated comment content."}
    another_user = User(
        id=str(uuid.uuid4()),  # Ensure unique ID
        email=f"anotheruser{uuid.uuid4()}@example.com",  # Unique email
        password="fakehashedpassword",
        first_name="Another",
        last_name="User"
    )
    db_session.add(another_user)
    db_session.commit()

    token = generate_token(another_user.id)  # Token for another user
    response = client.put(
        f"/comments/{create_test_comment.id}/",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "You do not have permission to update this comment."
