from api.v1.services.community import community_question_service
from fastapi import status
from fastapi.testclient import TestClient
import pytest
from main import app
from uuid_extensions import uuid7
from api.v1.services.user import user_service
from tests.v1.community.base import CREATE_QUESTION_ENDPOINT,mock_db_session,mock_question_service,create_mock_question,create_mock_user,mock_user_service
client = TestClient(app)



@pytest.mark.usefixtures("mock_db_session", "mock_question_service", "mock_user_service")
def test_create_question(mock_question_service, mock_db_session,mock_user_service):
    """Test for creating a community question."""
    mock_title = "Test Question"
    mock_message = "This is a test question"
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_user_id = mock_user.id
    mock_question = create_mock_question(mock_db_session, title=mock_title, message=mock_message, user_id=mock_user_id)
    mock_question_service.create_question.return_value = mock_question
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    response = client.post(
        CREATE_QUESTION_ENDPOINT,
        headers={'Authorization': f'Bearer {access_token}'},
        json={"title": mock_title, "message": mock_message, "user_id": mock_user_id}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "status_code": 201,
        "message": "Question created successfully",
        "success": True,
        "data": {
            "title": mock_question.title,
            "message": mock_question.message,
            "user_id": mock_question.id
        }
    }
