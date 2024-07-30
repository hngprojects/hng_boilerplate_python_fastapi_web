import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from api.db.database import get_db
from api.v1.models.comment import Comment
from api.v1.models.user import User
from api.v1.models.blog import Blog
from api.v1.schemas.comment import UpdateCommentRequest

client = TestClient(app)

# Dependency override to use a test database session
def override_get_db():
    from api.db.database import SessionLocal
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def db_session():
    from api.db.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def create_test_user(db_session):
    user = User(
        id="test_user_id",
        email="testuser@example.com",
        password="fakehashedpassword",
        first_name="Test",
        last_name="User"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def create_test_blog(db_session, create_test_user):
    blog = Blog(
        id="test_blog_id",
        title="Test Blog",
        content="This is a test blog.",
        user_id=create_test_user.id
    )
    db_session.add(blog)
    db_session.commit()
    return blog

@pytest.fixture
def create_test_comment(db_session, create_test_user, create_test_blog):
    comment = Comment(
        id="test_comment_id",
        content="This is a test comment.",
        user_id=create_test_user.id,
        blog_id=create_test_blog.id
    )
    db_session.add(comment)
    db_session.commit()
    return comment

def test_update_comment_success(db_session, create_test_user, create_test_comment):
    update_data = {
        "content": "Updated comment content."
    }
    response = client.put(
        f"/comments/{create_test_comment.id}/",
        json=update_data,
        headers={"Authorization": f"Bearer fake-jwt-token-for-{create_test_user.id}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Comment updated successfully."
    assert response_data["data"]["content"] == "Updated comment content."

def test_update_comment_not_found(db_session, create_test_user):
    update_data = {
        "content": "Updated comment content."
    }
    response = client.put(
        "/comments/non_existent_comment_id/",
        json=update_data,
        headers={"Authorization": f"Bearer fake-jwt-token-for-{create_test_user.id}"}
    )
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Comment not found."

def test_update_comment_unauthorized(db_session, create_test_user, create_test_comment):
    update_data = {
        "content": "Updated comment content."
    }
    another_user = User(
        id="another_user_id",
        email="anotheruser@example.com",
        password="fakehashedpassword",
        first_name="Another",
        last_name="User"
    )
    db_session.add(another_user)
    db_session.commit()
    
    response = client.put(
        f"/comments/{create_test_comment.id}/",
        json=update_data,
        headers={"Authorization": f"Bearer fake-jwt-token-for-{another_user.id}"}
    )
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "You do not have permission to update this comment."
