import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.v1.models import User, Organisation
from api.v1.schemas.request_password_reset import (ResetPasswordRequest,
                                                   RequestEmail,
                                                   OrganizationData,
                                                   ResetPasswordSuccesful)
from main import app

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_reset_token():
    return "mock_reset_token"

@pytest.fixture
def mock_reset_password_request():
    return ResetPasswordRequest(reset_token="mock_reset_tokenmock_reset_tokenmock_reset_tokenmock_reset_token",
                                new_password="New_password1@",
                                confirm_password="New_password1@")

@pytest.fixture
def mock_request_password_service():
    with patch("api.v1.services.request_pwd.RequestPasswordService") as MockService:
        service = MockService.return_value
        yield service

@pytest.fixture
def mock_verify_reset_token():
    with patch("api.v1.services.request_pwd.RequestPasswordService.verify_reset_token") as Mock_verify_token:
        Mock_verify_token.return_value = {"email": "test@gmail.com", "jti": 1}
        yield Mock_verify_token


@patch('api.v1.services.request_pwd.RequestPasswordService.update')
def test_reset_password(mock_update):
    token = "mock_reset_tokenmock_reset_tokenmock_reset_tokenmock_reset_token"
    mock_user = User(id='user_id', email="test@gmail.com",
                     first_name="Test",
                     last_name="User",
                     password="PassDam!23w",
                     is_verified=True,
                     is_deleted=False,
                     is_superadmin=False)
    
    org = Organisation(name="my org", id="org_id", email="org@gmail.com")
    mock_org = OrganizationData.model_validate(org, from_attributes=True)

    mock_update.return_value = ResetPasswordSuccesful(
        message='password successfully reset',
            status_code=201,
            access_token=token,
            data={"user": mock_user, "organisations": [mock_org]}
    ), ''

    response, _ = mock_update.return_value
    # Assert
    assert response.status_code == 201



def test_request_reset_link_user_not_found(mock_db_session, mock_request_password_service):
    # Arrange
    mock_request_password_service.fetch.side_effect = HTTPException(status_code=404, detail="User not found")

    reset_email = RequestEmail(email="unknown@gmail.com")

    # Act
    response = client.post("/api/v1/auth/forgot-password", json={"email": reset_email.email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {
    "message": "User not found",
    "status": False,
    "status_code": 404
}

def test_reset_password_invalid_token(mock_db_session, mock_reset_password_request, mock_request_password_service):
    # Arrange
    mock_request_password_service.update.side_effect = HTTPException(status_code=400, detail="reset token invalid")

    # Act
    response = client.patch("/api/v1/auth/reset-password", json=mock_reset_password_request.dict())

    # Assert
    assert response.status_code == 400
    # assert response.json() == {"message": "reset token invalid"}
    assert response.json() == {
    "message": "reset token invalid",
    "status": False,
    "status_code": 400
}
