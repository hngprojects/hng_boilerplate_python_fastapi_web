import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from api.v1.models.comment import Comment
from api.v1.models.user import User

client = TestClient(app)

@pytest.fixture
def mock_db_session(mocker):
    db_session = mocker.patch('api.db.database.SessionLocal', autospec=True)
    return db_session.return_value

@pytest.fixture
def create_test_comment(mock_db_session):
    comment = Comment(id="test_comment_id", blog_id="test_blog_id", content="Original content", created_at="2023-07-28T12:00:00")
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = comment
    mock_db_session.add(comment)
    mock_db_session.commit()
    return comment

@pytest.fixture
def create_test_user(mock_db_session):
    user = User(id="test_user_id", email="testuser@example.com", password="fakehashedpassword", first_name="Test", last_name="User")
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = user
    mock_db_session.add(user)
    mock_db_session.commit()
    return user

def generate_token(user_id):
    # Mock or generate a token for authentication
    return "your_jwt_token"

def test_update_comment_success(client, create_test_comment, create_test_user, mock_db_session):
    update_data = {"content": "Updated comment content."}
    token = generate_token(create_test_user.id)
    
    with patch('api.v1.routers.comments.get_current_user', return_value=create_test_user):
        response = client.patch(
            f"/comments/{create_test_comment.id}/",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["content"] == "Updated comment content."
    assert response_data["id"] == create_test_comment.id

def test_update_comment_not_found(client, create_test_user, mock_db_session):
    update_data = {"content": "Updated comment content."}
    token = generate_token(create_test_user.id)
    
    with patch('api.v1.routers.comments.get_current_user', return_value=create_test_user):
        response = client.patch(
            "/comments/non_existent_comment_id/",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Comment not found"

def test_update_comment_unauthorized(client, create_test_comment, mock_db_session):
    another_user = User(
        id="another_user_id",
        email="anotheruser@example.com",
        password="fakehashedpassword",
        first_name="Another",
        last_name="User"
    )
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = another_user
    mock_db_session.add(another_user)
    mock_db_session.commit()
    token = generate_token(another_user.id)
    
    with patch('api.v1.routers.comments.get_current_user', return_value=another_user):
        response = client.patch(
            f"/comments/{create_test_comment.id}/",
            json={"content": "Unauthorized update attempt."},
            headers={"Authorization": f"Bearer {token}"}
        )
        
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "You do not have permission to update this comment."
