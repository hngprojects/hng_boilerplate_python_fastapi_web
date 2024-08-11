from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.email_template import EmailTemplate
from api.v1.services.email_template import email_template_service
from main import app


def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        deleted_at=datetime.now(timezone.utc)
    )


def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_email_template():
    return EmailTemplate(
        id=str(uuid7()),
        title="Test name",
        type="Test name",
        template="<h1>Hello</h1>",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_delete_template_success(client, db_session_mock):
    '''Test to successfully delete an email template'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    app.dependency_overrides[email_template_service.delete] = lambda: mock_email_template

    # Mock email_template creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_template = mock_email_template()

    with patch("api.v1.services.email_template.email_template_service.delete", return_value=mock_template) as mock_delete:
        response = client.delete(
            f'/api/v1/email-templates/{mock_template.id}',
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 204

    
def test_delete_template_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''

    mock_template = mock_email_template()

    response = client.delete(
        f'/api/v1/email-templates/{mock_template.id}'
    )

    assert response.status_code == 401
