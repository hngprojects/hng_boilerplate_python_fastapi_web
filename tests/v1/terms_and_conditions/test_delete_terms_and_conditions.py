import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from unittest.mock import MagicMock, patch
from api.v1.models import TermsAndConditions, User
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from fastapi import status

client = TestClient(app)
URI = "/api/v1/terms-and-conditions"
LOGIN_URI = "/api/v1/auth/login"

test_terms_data = {
    "title": "My Terms and Conditions",
    "content": "My Content",
}

@pytest.fixture
def mock_db_session(_=MagicMock()):
    """Mock session"""
    with patch(get_db.__module__):
        app.dependency_overrides[get_db] = lambda: _
        yield _
    app.dependency_overrides = {}

def create_mock_super_admin(_):
    """Mock super admin"""
    _.query.return_value.filter.return_value.first.return_value = User(
        id=str(uuid7()),
        email="user@example.com",
        password=user_service.hash_password("P@ssw0rd"),
        is_super_admin=True,
    )

def create_mock_terms_and_conditions(_):
    """Mock terms and conditions"""
    _.query.return_value.filter.return_value.first.return_value = TermsAndConditions(
        id=str(uuid7()),
        title=test_terms_data["title"],
        content=test_terms_data["content"],
    )

theader = lambda _: {"Authorization": f"Bearer {_}"}

@pytest.mark.usefixtures("mock_db_session")
def test_delete_terms_and_conditions_success(mock_db_session):
    """Test successful deletion of terms and conditions"""
    create_mock_super_admin(mock_db_session)
    create_mock_terms_and_conditions(mock_db_session)

    # Log in to get the token
    tok = client.post(
        LOGIN_URI, json={"email": "user@example.com", "password": "P@ssw0rd"}
    ).json()
    assert tok["status_code"] == status.HTTP_200_OK
    token = tok["data"]["user"]["access_token"]

    # Get the ID of the mocked TermsAndConditions
    terms_id = mock_db_session.query.return_value.filter.return_value.first.return_value.id

    # Perform the delete request
    res = client.delete(f"{URI}/{terms_id}", headers=theader(token))

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {
        "message": "Terms and Conditions deleted successfully",
        "status_code": 200,
        "success": True,
        "terms_id": terms_id,
    }

@pytest.mark.usefixtures("mock_db_session")
def test_delete_terms_and_conditions_not_found(mock_db_session):
    """Test deletion when terms and conditions are not found"""
    create_mock_super_admin(mock_db_session)

    # Log in to get the token
    tok = client.post(
        LOGIN_URI, json={"email": "user@example.com", "password": "P@ssw0rd"}
    ).json()
    assert tok["status_code"] == status.HTTP_200_OK
    token = tok["data"]["user"]["access_token"]

    # Mock the service method to raise an HTTPException
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    # Perform the delete request with a non-existing ID
    res = client.delete(f"{URI}/non-existing-id", headers=theader(token))

    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert res.json() == {"detail": "Terms and Conditions not found"}

@pytest.mark.usefixtures("mock_db_session")
def test_delete_terms_and_conditions_internal_error(mock_db_session):
    """Test deletion when an unexpected error occurs"""
    create_mock_super_admin(mock_db_session)
    
    # Log in to get the token
    tok = client.post(
        LOGIN_URI, json={"email": "user@example.com", "password": "P@ssw0rd"}
    ).json()
    assert tok["status_code"] == status.HTTP_200_OK
    token = tok["data"]["user"]["access_token"]

    # Mock the service method to raise a generic exception
    mock_db_session.query.return_value.filter.return_value.first.side_effect = Exception("Unexpected error")

    # Perform the delete request
    res = client.delete(f"{URI}/1", headers=theader(token))

    assert res.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert res.json() == {"detail": {"message": "An unexpected error occurred", "status_code": 500, "success": False}}
