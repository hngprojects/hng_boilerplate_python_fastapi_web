from api.v1.services.community import community_question_service
from fastapi import status
from fastapi.testclient import TestClient
import pytest
from api.v1.services.user import user_service
from main import app
from tests.v1.community.base import create_mock_question,UPDATE_QUESTION_ENDPOINT,mock_db_session,mock_question_service
client = TestClient(app)

@pytest.mark.usefixtures("mock_db_session", "mock_question_service")
def test_update_question(mock_question_service, mock_db_session, mocker):
    """Test for updating a community question."""
    question_id = "1"
    update_data = {
        "title": "Updated Title",
        "message": "Updated message content",
        "user_id": "user1"
    }
    
    # Create mock user with appropriate permissions
    mock_user = mocker.Mock()
    mock_user.id = "user1"
    mock_user.is_admin = True
    
    # Create and configure mock question
    mock_question = create_mock_question(mock_db_session, question_id=question_id)
    mock_question.user_id = mock_user.id  # Make the user the owner
    mock_question.title = update_data["title"]
    mock_question.message = update_data["message"]
    
    # Mock the fetch_by_id method to return our question for ownership check
    mock_question_service.fetch_by_id.return_value = mock_question
    
    # Mock the update_question method
    mock_question_service.update_question.return_value = mock_question
    
    # Mock the user authentication dependency
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    try:
        response = client.put(
            UPDATE_QUESTION_ENDPOINT.format(question_id=question_id),
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "success"
        
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.pop(user_service.get_current_user, None)