import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Comment
from uuid_extensions import uuid7
from unittest.mock import MagicMock, patch

client = TestClient(app)

# Mock database session fixture
@pytest.fixture
def mock_db_session():
    db_session_mock = MagicMock(spec=Session)
    return db_session_mock

# Override the get_db dependency to use the mock database session
@pytest.fixture(autouse=True)
def override_get_db(mock_db_session):
    def _override_get_db():
        yield mock_db_session
    app.dependency_overrides[get_db] = _override_get_db

# Fixture for a test user
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )

# Fixture for a test comment
@pytest.fixture
def test_comment(test_user):
    return Comment(
        id=str(uuid7()),
        user_id=test_user.id,
        blog_id=str(uuid7()),
        content="Just a test comment",
    )

# Fixture for generating an access token
@pytest.fixture
def access_token_user1(test_user):
    return user_service.create_access_token(user_id=test_user.id)

# Test for successful comment deletion
def test_delete_comment_success(
    mock_db_session, 
    test_user, 
    test_comment,
    access_token_user1,
):
    def mock_get(model, ident):
        if model == Comment and ident == test_comment.id:
            return test_comment
        return None

    mock_db_session.get.side_effect = mock_get
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.delete(f"/api/v1/comments/{test_comment.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()['message'] == "Comment deleted successfully."
    mock_db_session.delete.assert_called_once_with(test_comment)

# Test for unauthorized access (no token)
def test_delete_comment_unauthorized(
    mock_db_session, 
    test_user, 
    test_comment,
):
    headers = {}  # No authorization header

    response = client.delete(f"/api/v1/comments/{test_comment.id}", headers=headers)

    assert response.status_code == 401  # Unauthorized access

# Test for internal server error during deletion
def test_delete_comment_internal_server_error(
    mock_db_session, 
    test_user, 
    test_comment,
    access_token_user1,
):
    def mock_get(model, ident):
        if model == Comment and ident == test_comment.id:
            return test_comment
        return None

    mock_db_session.get.side_effect = mock_get
    mock_db_session.delete.side_effect = Exception("Internal server error")

    # Ensuring the user has proper authorization to access the comment
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.delete(f"/api/v1/comments/{test_comment.id}", headers=headers)

    assert response.status_code == 500
    assert response.json()['message'] == "Internal server error."

# Test for comment not found
def test_delete_comment_not_found(
    mock_db_session, 
    test_user,
    access_token_user1,
):
    def mock_get(model, ident):
        return None  # Simulate that no comment exists with this ID

    mock_db_session.get.side_effect = mock_get

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.delete(f"/api/v1/comments/{str(uuid7())}", headers=headers)

    assert response.status_code == 404
    assert response.json()['message'] == "Comment does not exist"

# Test for invalid method
def test_delete_comment_invalid_method(
    mock_db_session, 
    test_user, 
    test_comment,
    access_token_user1,
):
    headers = {'Authorization': f'Bearer {access_token_user1}'}

    response = client.get(f"/api/v1/comments/{test_comment.id}", headers=headers)

    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

# Test for bad request with an invalid UUID
def test_delete_comment_bad_request(
    mock_db_session, 
    test_user,
    access_token_user1,
):
    invalid_uuid = "invalid-uuid"

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.delete(f"/api/v1/comments/{invalid_uuid}", headers=headers)

    assert response.status_code == 400
    assert response.json()['message'] == "An invalid request was sent."