# tests/test_comment.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_update_comment_success():
    response = client.put(
        "/api/v1/comments/1/",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Comment updated successfully."

def test_update_comment_invalid_input():
    response = client.put(
        "/api/v1/comments/1/",
        json={"content": ""},
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 400

def test_update_comment_unauthorized():
    response = client.put(
        "/api/v1/comments/1/",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
 
def test_update_comment_forbidden():
    response = client.put(
        "/api/v1/comments/another_user_comment_id/",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 403

def test_update_comment_not_found():
    response = client.put(
        "/api/v1/comments/nonexistent_comment_id/",
        json={"content": "Updated content"},
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 404
