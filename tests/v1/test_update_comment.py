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

@pytest.fixture
def create_test_comment(db_session):
    comment = Comment(id="test_comment_id", blog_id="test_blog_id", content="Original content", created_at="2023-07-28T12:00:00")
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
    # Mock or generate a token for authentication
    return "your_jwt_token"

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

from api.db.database import db_session

def test_update_comment_unauthorized(client, create_test_comment):
    another_user = User(
        id="another_user_id",
        email="anotheruser@example.com",
        password="fakehashedpassword",
        first_name="Another",
        last_name="User"
    )
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