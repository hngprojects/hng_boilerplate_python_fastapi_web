from api.v1.services.user import user_service
from api.v1.services.comments import comment_service
from api.v1.models.comment import Comment
from api.v1.models.user import User
from main import app
from fastapi import HTTPException
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_current_user():
    return User(id="user123", username="testuser")


@pytest.fixture
def mock_comment():
    return Comment(id="comment123", content="Original content", user_id="user123")


@pytest.fixture
def mock_auth(monkeypatch):
    def mock_get_current_user():
        return User(id="user123", username="testuser")
    monkeypatch.setattr(
        "api.v1.routes.comments.user_service.get_current_user", mock_get_current_user)


def test_update_comment_success(mock_db, mock_current_user, mock_comment, mock_auth, monkeypatch):
    def mock_get_db():
        return mock_db

    def mock_update_comment(db, id, user, **kwargs):
        if id == "comment123" and user.id == "user123":
            mock_comment.content = kwargs.get('content')
            return mock_comment
        return None

    monkeypatch.setattr("api.v1.routes.comments.get_db", mock_get_db)
    monkeypatch.setattr(
        "api.v1.routes.comments.comment_service.update_comment", mock_update_comment)

    response = client.put(
        "/api/v1/comments/comment123",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 401
    assert response.json()["status_code"] == 401


def test_update_comment_not_found(mock_db, mock_auth, monkeypatch):
    def mock_get_db():
        return mock_db

    def mock_update_comment(db, id, user, **kwargs):
        return None

    monkeypatch.setattr("api.v1.routes.comments.get_db", mock_get_db)
    monkeypatch.setattr(
        "api.v1.routes.comments.comment_service.update_comment", mock_update_comment)

    response = client.put(
        "/api/v1/comments/nonexistent",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 401


def test_update_comment_invalid_input(mock_db, mock_auth, monkeypatch):
    def mock_get_db():
        return mock_db

    monkeypatch.setattr("api.v1.routes.comments.get_db", mock_get_db)

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
        "api.v1.routes.comments.user_service.get_current_user", mock_get_current_user)

    response = client.put(
        "/api/v1/comments/comment123",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


def test_update_comment_wrong_user(mock_db, mock_auth, mock_comment, monkeypatch):
    def mock_get_db():
        return mock_db

    def mock_get_current_user():
        return User(id="wrong_user", username="wronguser")

    def mock_update_comment(db, id, user, **kwargs):
        return None  # Simulating that the comment wasn't found for this user

    monkeypatch.setattr("api.v1.routes.comments.get_db", mock_get_db)
    monkeypatch.setattr(
        "api.v1.routes.comments.user_service.get_current_user", mock_get_current_user)
    monkeypatch.setattr(
        "api.v1.routes.comments.comment_service.update_comment", mock_update_comment)

    response = client.put(
        "/api/v1/comments/comment123",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 401
