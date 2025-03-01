import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Blog, Comment, CommentDislike
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from unittest.mock import MagicMock

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

# Test User
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


@pytest.fixture
def test_blog(test_user):
    return Blog(
        id=str(uuid7()),
        author_id=test_user.id, 
        title="Test 1", 
        content="Test blog one"
    )

@pytest.fixture
def test_comment(test_user, test_blog):
    return Comment(
        id=str(uuid7()),
        user_id=test_user.id,
        blog_id=test_blog.id,
        content="Just a test comment",
    )

@pytest.fixture
def access_token_user1(test_user):
    return user_service.create_access_token(user_id=test_user.id)

# Test adding comment to blog
def test_dislike_comment(
    mock_db_session, 
    test_user, 
    test_blog, 
    test_comment,
    access_token_user1,
):
    # Mock the GET method for Organisation
    def mock_get(model, ident):
        if model == Comment and ident == test_comment.id:
            return test_comment
        return None

    mock_db_session.get.side_effect = mock_get

    # Mock the query to return test user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user
    
    # Mock the query to return null for existing dislikes
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = []

    # Test user belonging to the organisation
    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.post(f"/api/v1/comments/{test_comment.id}/dislike", headers=headers)
    
    # Debugging statement
    if response.status_code != 201:
        print(response.json())  # Print error message for more details

    assert response.status_code == 201, f"Expected status code 200, got {response.status_code}"
    assert response.json()['message'] == "Dislike added successfully"

def test_dislike_comment_twice(
    mock_db_session, 
    test_user, 
    test_blog, 
    test_comment,
    access_token_user1,
    mocker
):
    # Mock the GET method for Organisation
    def mock_get(model, ident):
        if model == Comment and ident == test_comment.id:
            return test_comment
        return None

    mock_db_session.get.side_effect = mock_get

    # # Mock the query to return test user
    # mock_db_session.query.return_value.filter.return_value.first.return_value = test_user
    
    # # Mock the query to return null for existing dislikes
    # mock_db_session.query.return_value.filter_by.return_value.first.return_value = [test_dislike_comment]

    # # Test user belonging to the organisation
    # headers = {'Authorization': f'Bearer {access_token_user1}'}
    # response = client.post(f"/api/v1/comments/{test_comment.id}/dislike", headers=headers)
    
    # # Debugging statement
    # if response.status_code != 201:
    #     print(response.json())  # Print error message for more details

    # assert response.status_code == 400, f"Expected status code 200, got {response.status_code}"
    # assert response.json()['message'] == "You can only dislike once"


    # Simulate that the user has not disliked the comment yet.
    mock_query = mocker.MagicMock()
    mock_query.filter_by.return_value.first.return_value = None
    mock_db_session.query.return_value = mock_query

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.post(f"/api/v1/comments/{test_comment.id}/dislike", headers=headers)
    
    # Print the error details if the status code is not as expected.
    if response.status_code != 201:
        print(response.json())


    # Check that the response status and message are as expected.
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    assert response.json()['message'] == "Comment disliked successfully!"

# Duplicate dislike test
def test_dislike_comment_twice(
    mock_db_session, 
    test_user, 
    test_blog, 
    test_comment,
    access_token_user1,
    mocker,
):
    # Simulate comment existence.
    def mock_get(model, ident):
        if model == Comment and ident == test_comment.id:
            return test_comment
        return None

    mock_db_session.get.side_effect = mock_get

    # Simulate that the user already disliked the comment.
    existing_dislike = CommentDislike(
        id=str(uuid7()),
        comment_id=test_comment.id,
        user_id=test_user.id,
        ip_address="127.0.0.1"
    )
    mock_query = mocker.MagicMock()
    mock_query.filter_by.return_value.first.return_value = existing_dislike
    mock_db_session.query.return_value = mock_query

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.post(f"/api/v1/comments/{test_comment.id}/dislike", headers=headers)
    
    # Print error details for debugging if needed.
    if response.status_code != 400:
        print(response.json())
    
    # Check that duplicate dislike attempts return the correct error.
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
    # The error response now uses the "detail" key.
    assert response.json()['message'] == "You can only dislike once"

