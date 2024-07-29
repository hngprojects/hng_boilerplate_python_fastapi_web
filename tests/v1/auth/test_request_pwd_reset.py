import sys
import os
import warnings
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from fastapi import Request
from api.v1.models.user import User
from api.v1.services.request_pwd import reset_service
from api.db.database import get_db
from sqlalchemy.exc import SQLAlchemyError

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app

REQUEST_PASSWORD_REQUEST_ENDPOINT = '/api/v1/auth/request-password-reset'
GET_PASSWORD_RESET_ENDPOINT = '/api/v1/auth/reset-password'
POST_PASSWORD_RESET_ENDPOINT = 'api/v1/auth/reset-password'

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_reset_service():
    with patch("api.v1.services.request_pwd.reset_service", autospec=True) as mock_service:
        yield mock_service

@pytest.fixture
def mock_verify_reset_token():
    with patch("api.v1.services.request_pwd.verify_reset_token", autospec=True) as mock_verify:
        yield mock_verify

@pytest.fixture
def mock_get_password_hash():
    with patch("api.v1.services.request_pwd.get_password_hash", autospec=True) as mock_hash:
        yield mock_hash

def create_mock_reset_link(mock_reset_service, user_email):
    mock_link = "mock_token"
    mock_reset_service.create.return_value = {"msg": "Password reset link sent"}
    return mock_link

def create_mock_verify_link(mock_reset_service, user_email):
    mock_link = "mock_token"
    mock_reset_service.process_reset_link.return_value = {"msg": "Token is valid", "email": user_email}
    return mock_link


def create_mock_user(mock_db_session, user_email):
    mock_user = User(
        id=1,
        email=user_email,
        password="hashed_password",
        first_name='Test',
        last_name='User',
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query(User).filter_by(email=user_email).first.return_value = mock_user
    return mock_user

@pytest.mark.usefixtures("mock_db_session", "mock_reset_service", "mock_verify_reset_token", "mock_get_password_hash")
def test_reset_password_success(mock_db_session, mock_verify_reset_token, mock_get_password_hash):
    user_email = "testuser@example.com"
    token = "mock_token"
    new_password = "Password@123"

    mock_verify_reset_token.return_value = user_email
    create_mock_user(mock_db_session, user_email)
    mock_get_password_hash.return_value = "hashed_new_password"

    payload = {
        "new_password": new_password,
        "confirm_new_password": new_password
    }

    response = client.post(POST_PASSWORD_RESET_ENDPOINT, params={"token": token}, json=payload)
    print("JSON", response.json())
    print("JSON", response.url)
    assert response.status_code == 200
    assert response.json()['message'] == "Password has been reset successfully"
    assert mock_db_session.commit.called


@pytest.mark.usefixtures("mock_db_session", "mock_reset_service", "mock_verify_reset_token")
def test_reset_password_invalid_token(mock_verify_reset_token):
    mock_verify_reset_token.return_value = None
    token = "invalid_token"
    payload = {
        "new_password": "Password@123",
        "confirm_new_password": "Password@123"
    }

    response = client.post(POST_PASSWORD_RESET_ENDPOINT, params={"token": token}, json=payload)
    assert response.status_code == 400
    assert response.json()['message'] == "Invalid or expired token"

@pytest.mark.usefixtures("mock_db_session", "mock_reset_service", "mock_verify_reset_token")
def test_reset_password_user_not_found(mock_db_session, mock_verify_reset_token):
    user_email = "testuser@example.com"
    token = "mock_token"
    mock_verify_reset_token.return_value = user_email
    mock_db_session.query(User).filter_by(email=user_email).first.return_value = None

    payload = {
        "new_password": "Password@123",
        "confirm_new_password": "Password@123"
    }

    response = client.post(POST_PASSWORD_RESET_ENDPOINT, params={"token": token}, json=payload)
    assert response.status_code == 404
    assert response.json()['message'] == "User not found"

def test_reset_password_passwords_do_not_match(mock_db_session, mock_verify_reset_token):
    user_email = "testuser@example.com"
    token = "mock_token"
    mock_verify_reset_token.return_value = user_email
    create_mock_user(mock_db_session, user_email)

    payload = {
        "new_password": "Password@123",
        "confirm_new_password": "Password@1234"
    }

    response = client.post(POST_PASSWORD_RESET_ENDPOINT, params={"token": token}, json=payload)
    assert response.status_code == 400
    assert response.json()['message'] == "Passwords do not match"

@pytest.mark.usefixtures("mock_db_session", "mock_reset_service", "mock_verify_reset_token")
def test_reset_password_database_error(mock_db_session, mock_verify_reset_token):
    user_email = "testuser@example.com"
    token = "mock_token"
    new_password = "Password@123"

    mock_verify_reset_token.return_value = user_email
    create_mock_user(mock_db_session, user_email)
    mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

    payload = {
        "new_password": new_password,
        "confirm_new_password": new_password
    }

    response = client.post(POST_PASSWORD_RESET_ENDPOINT, params={"token": token}, json=payload)
    assert response.status_code == 500
    assert response.json()['message'] == "An error occurred while processing your request."
    assert mock_db_session.rollback.called


@pytest.mark.usefixtures("mock_db_session", "mock_reset_service")
def test_create_valid_reset_link(mock_db_session, mock_reset_service):
    user_email = "mike@example.com"
    create_mock_reset_link(mock_reset_service, user_email)

    payload = {
        "user_email": user_email,
    }

    response = client.post(REQUEST_PASSWORD_REQUEST_ENDPOINT, json=payload)

    print("JSON", response.json())
    assert response.status_code == 201
    assert response.json()['message'] == "Password reset link sent successfully"


@pytest.mark.usefixtures("mock_db_session", "mock_reset_service")
def test_create_reset_link_invalid_email(mock_db_session, mock_reset_service):
    user_email = "miexample.com"
    create_mock_reset_link(mock_reset_service, user_email)

    payload = {
        "user_email": user_email,
    }

    response = client.post(REQUEST_PASSWORD_REQUEST_ENDPOINT, json=payload)

    print("JSON", response.json())
    assert response.status_code == 422
    assert response.json()['message'] == "Invalid input"
