from datetime import datetime, timezone
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.organization import Organization
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.services.organization import organization_service
from main import app


def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=False,
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
        is_super_admin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_organization():
    return Organization(
        id=str(uuid7()),
        company_name="Health Co",
        company_email="info@healthco.com",
        industry="Healthcare",
        organization_type="Public",
        country="USA",
        state="New York",
        address="456 Health Blvd",
        lga="Manhattan",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_csv_content():
    # Create a sample CSV content
    sample_csv_content = StringIO()
    sample_csv_content.write("ID,First name,Last name,Email,Date registered\n")
    sample_csv_content.write("1,John,Doe,john@example.com,2024-08-05T12:34:56\n")
    sample_csv_content.seek(0)

    return sample_csv_content



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


def test_export_success(client, db_session_mock):
    '''Test to successfully export user data in an organization'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    # app.dependency_overrides[organization_service.fetch] = lambda: mock_organization

    mock_org = mock_organization()
    db_session_mock.add(mock_org)
    db_session_mock.commit()

    mock_csv = mock_csv_content()

    with patch("api.v1.services.organization.organization_service.export_organization_members", return_value=mock_csv) as mock_export:
        response = client.get(
            f'/api/v1/organizations{mock_org.id}/users/export',
            headers={'Authorization': 'Bearer token'}
        )

        # Assert the response status code
        assert response.status_code == 200


def test_export_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''

    mock_org = mock_organization()
    db_session_mock.add(mock_org)
    db_session_mock.commit()
    
    response = client.get(
        f'/api/v1/organizations{mock_org.id}/users/export',
        headers={'Authorization': 'Bearer token'}
    )

    assert response.status_code == 401

