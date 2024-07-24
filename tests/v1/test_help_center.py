import sys
import os
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import HTTPException
from api.v1.routes.help_center import router
from ...main import app



# Mock in-memory database
mock_db = {}

def get_mock_db():
    return mock_db

def reset_mock_db():
    global mock_db
    mock_db = {}

client = TestClient(app)

# Define your secret key and algorithm
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_test_token(user_id="user123", expire_minutes=30):
    expiration = datetime.utcnow() + timedelta(minutes=expire_minutes)
    token_data = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token

admin_token = create_test_token(user_id="admin123")
invalid_token = "invalid.token"

@patch("api.v1.routes.help_center.get_db", side_effect=lambda: iter([get_mock_db()]))
@patch("api.v1.routes.help_center.get_current_admin", return_value={"user_id": "admin123"})
@patch("api.v1.routes.help_center.get_current_user", return_value={"user_id": "user123"})
def test_update_article_authorized(mock_get_current_user, mock_get_current_admin, mock_get_db):
    reset_mock_db()
    # Initialize mock database with test data
    db_article = {
        "id": "1",
        "title": "Initial Title",
        "content": "Initial Content",
        "author": "Author",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    get_mock_db()["1"] = db_article

    response = client.patch(
        "/help-center/topics/1",
        json={"title": "Updated Title", "content": "Updated Content"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "id": "1",
            "title": "Updated Title",
            "content": "Updated Content",
            "author": db_article["author"],
            "created_at": db_article["created_at"].isoformat(),
            "updated_at": db_article["updated_at"].isoformat(),
        },
        "status_code": 200
    }

@patch("api.v1.routes.help_center.get_db", side_effect=lambda: iter([get_mock_db()]))
@patch("api.v1.routes.help_center.get_current_admin", side_effect=HTTPException(status_code=403, detail="Forbidden"))
@patch("api.v1.routes.help_center.get_current_user", return_value={"user_id": "user123"})
def test_update_article_unauthorized(mock_get_current_user, mock_get_current_admin, mock_get_db):
    reset_mock_db()
    # Initialize mock database with test data
    get_mock_db()["1"] = {
        "id": "1",
        "title": "Initial Title",
        "content": "Initial Content",
        "author": "Author",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    response = client.patch(
        "/help-center/topics/1",
        json={"title": "Updated Title", "content": "Updated Content"},
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}

@patch("api.v1.routes.help_center.get_db", side_effect=lambda: iter([get_mock_db()]))
@patch("api.v1.routes.help_center.get_current_admin", return_value={"user_id": "admin123"})
@patch("api.v1.routes.help_center.get_current_user", return_value={"user_id": "user123"})
def test_update_article_input_validation(mock_get_current_user, mock_get_current_admin, mock_get_db):
    reset_mock_db()
    # Initialize mock database with test data
    get_mock_db()["1"] = {
        "id": "1",
        "title": "Initial Title",
        "content": "Initial Content",
        "author": "Author",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    response = client.patch(
        "/help-center/topics/1",
        json={"title": "", "content": "Updated Content"},  # Invalid title
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 422  # Unprocessable Entity, or a similar validation error code
