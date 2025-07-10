from api.v1.services.community import community_question_service
from fastapi import status
from fastapi.testclient import TestClient
import pytest
from main import app
from api.v1.services.user import user_service
from tests.v1.community.base import create_mock_question,MARK_RESOLVED_ENDPOINT,mock_db_session,mock_question_service
client = TestClient(app)


@pytest.mark.usefixtures("mock_db_session", "mock_question_service")
def test_mark_question_resolved(mock_question_service, mock_db_session, mocker):
    """Test for marking a community question as resolved."""
    question_id = "1"
    is_resolved = True
    
    # Create mock user with admin privileges to bypass permission check
    mock_user = mocker.Mock()
    mock_user.id = "user1"
    mock_user.is_admin = True
    
    # Create mock question
    mock_question = create_mock_question(mock_db_session, question_id=question_id)
    mock_question.user_id = mock_user.id  # Make the mock user the owner
    mock_question.is_resolved = is_resolved
    
    # Mock the fetch_by_id method
    mock_question_service.fetch_by_id.return_value = mock_question
    
    # Mock the mark_as_resolved method
    mock_question_service.mark_as_resolved.return_value = mock_question
    
    # Mock the user authentication dependency
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    try:
        response = client.patch(
            MARK_RESOLVED_ENDPOINT.format(question_id=question_id),
            json={"is_resolved": is_resolved}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["is_resolved"] == True
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.pop(user_service.get_current_user, None)