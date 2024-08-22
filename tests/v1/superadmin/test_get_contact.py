import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.v1.models.contact_us import ContactUs
from sqlalchemy.orm import Session
from api.db.database import get_db
from unittest import mock
from api.v1.models.associations import user_organisation_association
from sqlalchemy import insert

client = TestClient(app)


# Mock the database session dependency
@pytest.fixture
def mock_db_session(mocker=mock):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock


# Test fixtures for users and access tokens
@pytest.fixture
def test_admin():
    return User(
        id="admin_id",  # Ensure the admin has an ID
        email="admin@example.com",
        is_superadmin=True,
    )


@pytest.fixture
def test_message():
    return ContactUs(
        id="message_id",
        org_id="org_id",
        full_name="John Doe",
        email="johndoe@example.com",
        title="Query",
        message="Short message content"
    )


@pytest.fixture
def access_token_admin(test_admin):
    return user_service.create_access_token(test_admin.id)


# Test successful customer update
def test_get_message(mock_db_session, test_message, access_token_admin, test_admin):
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [test_admin]
    mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [test_message]
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = 'admin'

    headers = {'Authorization': f'Bearer {access_token_admin}'}

    response = client.get(f"/api/v1/contact/{test_message.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()['data']['full_name'] == test_message.full_name
    assert response.json()['data']['email'] == test_message.email
    assert response.json()['data']['title'] == test_message.title
    assert response.json()['data']['message'] == test_message.message


def test_invalid_id(mock_db_session, test_message, access_token_admin, test_admin):
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [test_admin]
    mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [None]
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = 'admin'

    headers = {'Authorization': f'Bearer {access_token_admin}'}

    response = client.get(f"/api/v1/contact/invalid_id", headers=headers)
    assert response.status_code == 404


# Test unauthorized access
def test_unauthorized(mock_db_session, test_message, test_admin):
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [test_admin]
    mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [test_message]
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = 'admin'

    response = client.get(f"/api/v1/contact/{test_message.id}")
    assert response.status_code == 401  # Expecting 401 Unauthorized
