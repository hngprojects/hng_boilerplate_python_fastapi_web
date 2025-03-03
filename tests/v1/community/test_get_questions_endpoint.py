import pytest
from fastapi import status
from fastapi.testclient import TestClient
import pytest
from api.v1.services.user import user_service
from api.v1.services.community import community_question_service
from uuid_extensions import uuid7
from main import app
from tests.v1.community.base import create_mock_user,mock_user_service,create_mock_question,GET_ALL_QUESTIONS_ENDPOINT,GET_QUESTION_BY_ID_ENDPOINT,GET_QUESTIONS_BY_USER_ENDPOINT,mock_db_session,mock_question_service
from api.db.database import get_db
client = TestClient(app)

@pytest.mark.usefixtures("mock_db_session", "mock_question_service","mock_user_service")
def test_get_all_questions(mock_question_service, mock_db_session):
    """Test for fetching all community questions."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_questions = [
        create_mock_question(mock_db_session, question_id="1"),
        create_mock_question(mock_db_session, question_id="2", title="Another Question")
    ]
    mock_question_service.fetch_all.return_value = mock_questions
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    response = client.get(GET_ALL_QUESTIONS_ENDPOINT,
                          headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] == True

@pytest.mark.usefixtures("mock_db_session", "mock_question_service",)
def test_get_question_by_id(mock_question_service, mock_db_session):
    """Test for fetching a community question by ID."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_question = create_mock_question(
        mock_db_session, 
        title="Test Question", 
        message="This is a test question", 
        user_id=mock_user.id
    )
    response = client.get(GET_QUESTION_BY_ID_ENDPOINT.format(question_id=mock_question.id))
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] == True

@pytest.mark.usefixtures("mock_db_session", "mock_question_service")
def test_get_questions_by_user(mock_question_service, mock_db_session):
    """Test for fetching community questions by user ID."""
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    user_id = mock_user.id
    mock_questions = [
        create_mock_question(mock_db_session, question_id="1", user_id=user_id),
        create_mock_question(mock_db_session, question_id="2", title="Another Question", user_id=user_id)
    ]

    mock_question_service.fetch_by_user_id.return_value = mock_questions
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    response = client.get(GET_QUESTIONS_BY_USER_ENDPOINT.format(user_id=mock_questions[0].user_id),
                          headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == status.HTTP_200_OK
    assert mock_questions[0].user_id == mock_questions[1].user_id
    assert response.json()["success"] == True
    app.dependency_overrides.pop(user_service.get_current_user, None)

@pytest.mark.usefixtures("mock_db_session")
def test_get_question_not_found(mock_db_session):
    """Test for fetching a non-existent community question."""
    question_id = "3f3iiuefuin3"

    # Properly override the dependency function
    def override_get_db():
        return mock_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Properly mock the service function
    original_fetch_by_id = community_question_service.fetch_by_id
    community_question_service.fetch_by_id = lambda db, question_id: None
    
    try:
        response = client.get(GET_QUESTION_BY_ID_ENDPOINT.format(question_id=question_id))
        # Assert the expected 404 response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["status"] == False
    finally:
        # Restore the original function
        community_question_service.fetch_by_id = original_fetch_by_id
        app.dependency_overrides.pop(get_db, None)