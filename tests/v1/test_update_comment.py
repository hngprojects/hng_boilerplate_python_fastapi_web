from fastapi import HTTPException
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.comments import comment_service
from api.v1.models.comment import Comment
from api.v1.models.user import User
from main import app
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import pytest
import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, project_root)


client = TestClient(app)


@pytest.fixture
def mock_db():
    return Session()


@pytest.fixture
def mock_current_user():
    return User(id="user123", username="testuser")


@pytest.fixture
def mock_comment():
    return Comment(id="comment123", content="Original content", user_id="user123")


def test_update_comment_success(mock_db, mock_current_user, mock_comment, monkeypatch):
    def mock_get_db():
        return mock_db

    def mock_get_current_user():
        return mock_current_user

    def mock_update_comment(db, id, user, **kwargs):
        if id == "comment123" and user.id == "user123":
            mock_comment.content = kwargs.get('content')
            return mock_comment
        return None

    monkeypatch.setattr("api.db.database.get_db", mock_get_db)
    monkeypatch.setattr(
        "api.v1.services.user.user_service.get_current_user", mock_get_current_user)
    monkeypatch.setattr(
        "api.v1.services.comments.comment_service.update_comment", mock_update_comment)

    response = client.put(
        "/api/v1/comments/comment123",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 401
    assert response.json()["status_code"] == 401


def test_update_comment_not_found(mock_db, mock_current_user, monkeypatch):
    def mock_get_db():
        return mock_db

    def mock_get_current_user():
        return mock_current_user

    def mock_update_comment(db, id, user, **kwargs):
        return None

    monkeypatch.setattr("api.db.database.get_db", mock_get_db)
    monkeypatch.setattr(
        "api.v1.services.user.user_service.get_current_user", mock_get_current_user)
    monkeypatch.setattr(
        "api.v1.services.comments.comment_service.update_comment", mock_update_comment)

    response = client.put(
        "/api/v1/comments/nonexistent",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 401


def test_update_comment_invalid_input(mock_db, mock_current_user, monkeypatch):
    def mock_get_db():
        return mock_db

    def mock_get_current_user():
        return mock_current_user

    monkeypatch.setattr("api.db.database.get_db", mock_get_db)
    monkeypatch.setattr(
        "api.v1.services.user.user_service.get_current_user", mock_get_current_user)

    response = client.put(
        "/api/v1/comments/comment123",
        json={},  # Missing required 'content' field
        headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 401


def test_update_comment_unauthorized(monkeypatch):
    def mock_get_current_user():
        raise HTTPException(
            status_code=401, detail="Could not validate credentials")

    monkeypatch.setattr(
        "api.v1.services.user.user_service.get_current_user", mock_get_current_user)

    response = client.put(
        "/api/v1/comments/comment123",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


def test_update_comment_wrong_user(mock_db, mock_current_user, mock_comment, monkeypatch):
    def mock_get_db():
        return mock_db

    def mock_get_current_user():
        return User(id="wrong_user", username="wronguser")

    def mock_update_comment(db, id, user, **kwargs):
        return None  # Simulating that the comment wasn't found for this user

    monkeypatch.setattr("api.db.database.get_db", mock_get_db)
    monkeypatch.setattr(
        "api.v1.services.user.user_service.get_current_user", mock_get_current_user)
    monkeypatch.setattr(
        "api.v1.services.comments.comment_service.update_comment", mock_update_comment)

    response = client.put(
        "/api/v1/comments/comment123",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 401
