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
        updated_at=datetime.now(timezone.utc)
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
    return [
        EmailTemplate(
            id=str(uuid7()),
            title="Test name",
            type="Test name",
            template="<h1>Hello</h1>",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        EmailTemplate(
            id=str(uuid7()),
            title="Test name",
            type="Test name",
            template="<h1>Hello</h1>",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        EmailTemplate(
            id=str(uuid7()),
            title="Test name",
            type="Test name",
            template="<h1>Hello</h1>",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    ]


@pytest.fixture
def mock_db_session():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_get_all_email_templates(mock_db_session, client):
    """Test to verify the pagination response for email_templates."""

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    app.dependency_overrides[email_template_service.create] = lambda: mock_email_template

    # Mock data
    mock_templates = mock_email_template()

    mock_query = MagicMock()
    mock_query.count.return_value = 3
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_templates

    mock_db_session.query.return_value = mock_query

    # Perform the GET request
    response = client.get(
        '/api/v1/email-templates', 
        params={'limit': 2, 'skip': 0},
        headers={'Authorization': 'Bearer token'}
    )

    # Verify the response
    assert response.status_code == 200


def test_get_all_email_templates_with_skip(mock_db_session, client):
    """Test to verify the pagination response for email_templates."""

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    app.dependency_overrides[email_template_service.create] = lambda: mock_email_template

    # Mock data
    mock_templates = mock_email_template()
    
    mock_query = MagicMock()
    mock_query.count.return_value = 3
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_templates

    mock_db_session.query.return_value = mock_query


    # Perform the GET request
    response = client.get(
        '/api/v1/email-templates', 
        params={'limit': 2, 'skip': 2},
        headers={'Authorization': 'Bearer token'}
    )

    # Verify the response
    assert response.status_code == 200

    
def test_fetch_all_template_unauthorized(client, mock_db_session):
    '''Test for unauthorized user'''

    response = client.get(
        '/api/v1/email-templates',
    )

    assert response.status_code == 401