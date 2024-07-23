import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import HTTPException
from ...main import app
# from api.utils.dependencies import get_current_admin
from datetime import datetime




# Mock in-memory database
mock_db = {}

def get_mock_db():
    return mock_db

def reset_mock_db():
    global mock_db
    mock_db = {}

client = TestClient(app)

# Mock JWT token 
valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lI"

@patch("main.get_db", side_effect=lambda: iter([get_mock_db()]))
@patch("main.get_current_admin", return_value={"user_id": "admin123"})
def test_update_article_authorized(mock_get_db, mock_get_current_admin):
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
        headers={"Authorization": f"Bearer {valid_token}"}
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

@patch("main.get_db", side_effect=lambda: iter([get_mock_db()]))
@patch("main.get_current_admin", side_effect=HTTPException(status_code=403, detail="Forbidden"))
def test_update_article_unauthorized(mock_get_db, mock_get_current_admin):
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

@patch("main.get_db", side_effect=lambda: iter([get_mock_db()]))
@patch("main.get_current_admin", return_value={"user_id": "admin123"})
def test_update_article_input_validation(mock_get_db, mock_get_current_admin):
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
        headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 422  # Unprocessable Entity, or a similar validation error code