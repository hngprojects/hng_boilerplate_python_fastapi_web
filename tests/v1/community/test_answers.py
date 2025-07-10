import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.community import CommunityAnswer, CommunityQuestion
from api.v1.services.community import community_answer_service, community_question_service
from api.v1.services.user import user_service
from api.db.database import get_db
from fastapi import status
from uuid_extensions import uuid7
from tests.v1.community.base import create_mock_user,mock_user_service
client = TestClient(app)

# API Endpoints
CREATE_ANSWER_ENDPOINT = '/api/v1/community/answers/create'
GET_ALL_ANSWERS_ENDPOINT = '/api/v1/community/answers'
GET_ANSWER_BY_ID_ENDPOINT = '/api/v1/community/answers/{answer_id}'
GET_ANSWERS_BY_QUESTION_ENDPOINT = '/api/v1/community/answers/question/{question_id}'
GET_ANSWERS_BY_USER_ENDPOINT = '/api/v1/community/answers/user/{user_id}'
UPDATE_ANSWER_ENDPOINT = '/api/v1/community/answers/{answer_id}'
MARK_ACCEPTED_ENDPOINT = '/api/v1/community/answers/{answer_id}/accept'
DELETE_ANSWER_ENDPOINT = '/api/v1/community/answers/{answer_id}'

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_answer_service():
    """Fixture to create a mock community answer service."""
    with patch("api.v1.services.community.community_answer_service", autospec=True) as mock_service:
        yield mock_service

@pytest.fixture
def mock_question_service():
    """Fixture to create a mock community question service."""
    with patch("api.v1.services.community.community_question_service", autospec=True) as mock_service:
        yield mock_service

@pytest.fixture
def mock_auth_user():
    """Fixture to create a mock authenticated user."""
    mock_user = MagicMock()
    mock_user.id = "101"
    mock_user.is_admin = True
    
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    yield mock_user
    if user_service.get_current_user in app.dependency_overrides:
        app.dependency_overrides.pop(user_service.get_current_user)

def create_mock_answer(mock_db_session, answer_id="1", message="Test answer", user_id="101", question_id="201", is_accepted=False):
    """Create a mock community answer in the mock database session."""
    mock_answer = CommunityAnswer(
        id=answer_id,
        message=message,
        user_id=user_id,
        question_id=question_id,
        is_accepted=is_accepted,
        timestamp="2023-01-01T00:00:00"
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_answer
    return mock_answer

def create_mock_question(mock_db_session, question_id="201", title="Test Question", message="Test message", user_id="101"):
    """Create a mock community question for testing answers."""
    mock_question = CommunityQuestion(
        id=question_id,
        title=title,
        message=message,
        user_id=user_id,
        timestamp="2023-01-01T00:00:00"
    )
    return mock_question

# Test cases for each service method
@pytest.mark.usefixtures("mock_db_session", "mock_answer_service", "mock_user_service")
def test_create_answer(mock_answer_service, mock_db_session, mock_user_service):
    """Test for creating a community answer."""
    mock_message = "This is a test answer"
    mock_question_id = "201"
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    mock_answer = create_mock_answer(
        mock_db_session, 
        message=mock_message, 
        user_id=mock_user.id, 
        question_id=mock_question_id
    )
    mock_answer_service.create_answer.return_value = mock_answer
    access_token = user_service.create_access_token(user_id=str(uuid7()))
    
    response = client.post(
        CREATE_ANSWER_ENDPOINT,
        headers={'Authorization': f'Bearer {access_token}'},
        json={"message": mock_message,"user_id": mock_user.id,"question_id": mock_question_id}
    )

    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["status_code"] == 201
    assert response.json()["status"] == "success"
    assert "data" in response.json()
    assert response.json()["data"]["message"] == mock_message
    assert response.json()["data"]["question_id"] == mock_question_id
    

@pytest.mark.usefixtures("mock_db_session", "mock_answer_service")
def test_get_answers_by_question(mock_answer_service, mock_db_session):
    """Test for fetching community answers by question ID."""
    question_id = "201"
    mock_answers = [
        create_mock_answer(mock_db_session, answer_id="1", question_id=question_id),
        create_mock_answer(mock_db_session, answer_id="2", message="Another answer", question_id=question_id)
    ]
    mock_answer_service.fetch_by_question_id.return_value = mock_answers
    
    response = client.get(GET_ANSWERS_BY_QUESTION_ENDPOINT.format(question_id=question_id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"

@pytest.mark.usefixtures("mock_db_session", "mock_answer_service", "mock_auth_user")
def test_get_answers_by_user(mock_answer_service, mock_db_session, mock_auth_user):
    """Test for fetching community answers by user ID."""
    user_id = mock_auth_user.id
    mock_answers = [
        create_mock_answer(mock_db_session, answer_id="1", user_id=user_id),
        create_mock_answer(mock_db_session, answer_id="2", message="Another answer", user_id=user_id)
    ]
    mock_answer_service.fetch_by_user_id.return_value = mock_answers
    
    response = client.get(GET_ANSWERS_BY_USER_ENDPOINT.format(user_id=user_id))
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"

@pytest.mark.usefixtures("mock_db_session", "mock_answer_service", "mock_auth_user")
def test_update_answer(mock_answer_service, mock_db_session, mock_user_service):
    """Test for updating a community answer."""
    answer_id = "1"
    mock_user = create_mock_user(mock_user_service, mock_db_session)
    update_data = {
        "message": "Updated answer content",
        "user_id": mock_user.id,  # Include this since the route requires it
        "question_id": "201"  # Include this since the route requires it
    }
    
    mock_answer = create_mock_answer(mock_db_session, answer_id=answer_id, user_id=mock_user.id)
    mock_answer.message = update_data["message"]
    
    # Mock fetch_by_id to return the answer for ownership check
    mock_answer_service.fetch_by_id.return_value = mock_answer
    mock_answer_service.update_answer.return_value = mock_answer
    
    response = client.put(
        UPDATE_ANSWER_ENDPOINT.format(answer_id=answer_id),
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["message"] == update_data["message"]

@pytest.mark.usefixtures("mock_db_session", "mock_answer_service", "mock_question_service", "mock_auth_user")
def test_mark_answer_accepted(mock_answer_service, mock_db_session, mock_question_service, mock_auth_user):
    """Test for marking a community answer as accepted."""
    answer_id = "1"
    question_id = "201"
    is_accepted = True
    
    # Create mock answer and question
    mock_answer = create_mock_answer(mock_db_session, answer_id=answer_id, question_id=question_id)
    mock_question = create_mock_question(mock_db_session, question_id=question_id, user_id=mock_auth_user.id)
    
    # Mock fetch_by_id for both answer and question
    mock_answer_service.fetch_by_id.return_value = mock_answer
    mock_question_service.fetch_by_id.return_value = mock_question
    
    # Mock mark_as_accepted
    mock_answer.is_accepted = is_accepted
    mock_answer_service.mark_as_accepted.return_value = mock_answer
    
    response = client.patch(
        MARK_ACCEPTED_ENDPOINT.format(answer_id=answer_id),
        json={"is_accepted": is_accepted}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["is_accepted"] == is_accepted

@pytest.mark.usefixtures("mock_db_session", "mock_answer_service", "mock_auth_user")
def test_delete_answer(mock_answer_service, mock_db_session, mock_auth_user):
    """Test for deleting a community answer."""
    answer_id = "1"
    
    # Create mock answer for ownership check
    mock_answer = create_mock_answer(mock_db_session, answer_id=answer_id, user_id=mock_auth_user.id)
    mock_answer_service.fetch_by_id.return_value = mock_answer
    
    delete_result = {"status": "success", "detail": f"Answer with ID {answer_id} deleted successfully"}
    mock_answer_service.delete_answer.return_value = delete_result
    
    response = client.delete(DELETE_ANSWER_ENDPOINT.format(answer_id=answer_id))
    
    assert response.status_code == status.HTTP_200_OK