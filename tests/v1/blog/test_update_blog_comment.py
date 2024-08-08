import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Blog, Comment
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
def test_user_1():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )


# Test Super admin 
@pytest.fixture
def test_user_2():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )

# Test Blog 
@pytest.fixture
def test_blog(test_user_1):
    return Blog(
        id=str(uuid7()),
        author_id=test_user_1.id,
        title="test blog",
        content="testing blog 1, 2, 3.."
    )

# Test Comment
@pytest.fixture
def test_comment(test_user_1, test_blog):
    return Comment(
        id=str(uuid7()),
        user_id=test_user_1.id,
        blog_id=test_blog.id,
        content="Testing 1, 2, 3... "
    )

@pytest.fixture
def update_url(test_blog, test_comment):
    return {
        "both_exists": f"/api/v1/blogs/{test_blog.id}/comments/{test_comment.id}",
        "blog_exists": f"/api/v1/blogs/{test_blog.id}/comments/898989",
        "comment_exists": f"/api/v1/blogs/898989/comments/{test_comment.id}"
    }

# defining the update request body
comment_content = {"content": "Updated blog comment"}

# Access token for test user 1
@pytest.fixture
def test_user_1_access_token(test_user_1):
    return user_service.create_access_token(user_id=test_user_1.id)

# Access token for test user 2
@pytest.fixture
def test_user_2_access_token(test_user_2):
    return user_service.create_access_token(user_id=test_user_2.id)

# Test updating comment with the test_user_1 who created the comment
def test_comment_update_by_comment_author(
    mock_db_session, 
   test_user_1,
   test_blog,
   test_comment,
   test_user_1_access_token,
   update_url
):
    # Mock the GET method for Blog ID and Comment ID
    def mock_get(model, ident):
        if model == Blog and ident == test_blog.id:
            return test_blog
        elif model == Comment and ident == test_comment.id:
            return test_comment
        return None

    mock_db_session.get.side_effect = mock_get

    # Mock the query to return test user 1
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user_1

    # Test updating comment
    headers = {'Authorization': f'Bearer {test_user_1_access_token}'}
    response = client.put(update_url['both_exists'], headers=headers, json=comment_content)

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json()['message'] == "Blog comment updated successfully"
    assert response.json()['data']['content'] == comment_content['content']

# Test updating comment with the test_user_2 who did not create the test_comment
def test_comment_update_by_non_comment_author(
    mock_db_session, 
   test_user_2,
   test_blog,
   test_comment,
   test_user_2_access_token,
   update_url
):
    # Mock the GET method for Blog ID and Comment ID
    def mock_get(model, ident):
        if model == Blog and ident == test_blog.id:
            return test_blog
        elif model == Comment and ident == test_comment.id:
            return test_comment
        return None

    mock_db_session.get.side_effect = mock_get

    # Mock the query to return test user 1
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user_2
 
    # Test updating comment
    headers = {'Authorization': f'Bearer {test_user_2_access_token}'}
    response = client.put(update_url['both_exists'], headers=headers, json=comment_content)
    
    assert response.status_code == 403, f"Expected status code 403, got {response.status_code}"
    assert response.json()["message"] == "You are not authorized to update this comment"

# Test updating comment with the test_user_2 who did not create the test_comment
def test_non_existing_comment_id(
    mock_db_session, 
   test_user_2,
   test_blog,
   test_comment,
   test_user_2_access_token,
   update_url
):
    # Mock the GET method for Blog ID and Comment ID
    def mock_get(model, ident):
        if model == Blog and ident == test_blog.id:
            return test_blog
        elif model == Comment and ident == test_comment.id:
            return test_comment
        return None

    mock_db_session.get.side_effect = mock_get

    # Mock the query to return test user 1
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user_2
 
    # Test non existing Comment ID
    headers = {'Authorization': f'Bearer {test_user_2_access_token}'}
    response = client.put(update_url['blog_exists'], headers=headers, json=comment_content)
    
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    assert response.json()["message"] == "Comment does not exist"

    # Test non existing Blog ID
    response = client.put(update_url['comment_exists'], headers=headers, json=comment_content)

    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    assert response.json()["message"] == "Blog does not exist"



