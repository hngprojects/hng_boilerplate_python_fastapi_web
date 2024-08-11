import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Blog
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
def access_token_user1(test_user):
    return user_service.create_access_token(user_id=test_user.id)

# Test adding comment to blog
def test_add_comment_to_blog(
    mock_db_session, 
    test_user, 
    test_blog, 
    access_token_user1,
):
    # Mock the GET method for Organisation
    def mock_get(model, ident):
        if model == Blog and ident == test_blog.id:
            return test_blog
        return None

    mock_db_session.get.side_effect = mock_get

    # Mock the query for checking if user is in the organisation
    mock_db_session.query().return_value = test_blog

    # Test user belonging to the organisation
    content = {"content": "Test comment"}
    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.post(f"/api/v1/blogs/{test_blog.id}/comments", headers=headers, json=content)
    
    # Debugging statement
    if response.status_code != 201:
        print(response.json())  # Print error message for more details

    assert response.status_code == 201, f"Expected status code 200, got {response.status_code}"
    assert response.json()['message'] == "Comment added successfully!"
    assert response.json()['data']['blog_id'] == test_blog.id

