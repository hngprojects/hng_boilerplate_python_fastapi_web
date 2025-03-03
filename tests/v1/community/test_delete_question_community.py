from fastapi import status
from fastapi.testclient import TestClient
import pytest
from main import app
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from tests.v1.community.base import DELETE_QUESTION_ENDPOINT,mock_question_service,mock_db_session,create_mock_user,mock_user_service,create_mock_question,CREATE_QUESTION_ENDPOINT
client = TestClient(app)


@pytest.mark.usefixtures("mock_db_session", "mock_question_service", "mock_user_service")
def test_delete_question(mock_question_service, mock_db_session, mock_user_service):
    # Create mock user and question
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_question = create_mock_question(
        mock_db_session, 
        title="Test Question", 
        message="This is a test question", 
        user_id=mock_user.id
    )
    
    # Set up the mock service to return success for delete operation
    mock_question_service.delete_question.return_value = {
        "status": "success", 
        "detail": f"Question with ID {mock_question.id} deleted successfully"
    }
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    # Create an access token for authorization
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    
    # Make the DELETE request
    response = client.delete(
        DELETE_QUESTION_ENDPOINT.format(question_id=mock_question.id),
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status_code": 200,
        "message": f"Question with ID {mock_question.id} deleted successfully",
        "success": True,
    }
    
    app.dependency_overrides.pop(user_service.get_current_user, None)