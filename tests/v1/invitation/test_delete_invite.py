import sys
import os
import warnings
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from uuid_extensions import uuid7

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app
from api.v1.models.user import User
from api.v1.models.invitation import Invitation
from api.v1.models.organization import Organization
from api.v1.services.user import user_service
from api.db.database import get_db

DELETE_INVITE_ENDPOINT = '/api/v1/invite/{id}'

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_invite_service():
    with patch("api.v1.services.invite.invite_service", autospec=True) as mock_service:
        yield mock_service

def create_mock_user(mock_db_session, user_id):
    mock_user = User(
        id=user_id,
        email="testuser@gmail.com",
        password="hashed_password",
        first_name='Test',
        last_name='User',
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query(User).filter_by(id=user_id).first.return_value = mock_user
    return mock_user

def create_mock_organization(mock_db_session, org_id):
    mock_org = Organization(
        id=org_id,
        name="Test Organization",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query(Organization).filter_by(id=org_id).first.return_value = mock_org
    return mock_org

def create_mock_invitation(mock_db_session, user_id, org_id, invitation_id, expiration, is_valid):
    mock_invitation = Invitation(
        id=invitation_id,
        user_id=user_id,
        organization_id=org_id,
        expires_at=expiration,
        is_valid=is_valid
    )
    mock_db_session.query(Invitation).filter_by(id=invitation_id, is_valid=True).first.return_value = mock_invitation
    return mock_invitation

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_delete_invite_invalid_id(mock_db_session, mock_invite_service):
    user_id = str(uuid7())
    access_token = user_service.create_access_token(str(user_id))
    
    response = client.delete('/api/v1/invite', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 404

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_delete_invite_success(mock_db_session, mock_invite_service):
    user_id = str(uuid7())
    org_id = str(uuid7())
    id = str(uuid7())

    create_mock_user(mock_db_session, user_id)
    create_mock_organization(mock_db_session, org_id)
    create_mock_invitation(mock_db_session, user_id, org_id, id, datetime.now(timezone.utc), is_valid=True)
    
    access_token = user_service.create_access_token(str(user_id))
    
    response = client.delete(DELETE_INVITE_ENDPOINT.format(id=id), headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 204


@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_delete_invite_no_authorization(mock_db_session, mock_invite_service):
    user_id = str(uuid7())
    org_id = str(uuid7())
    id = str(uuid7())

    create_mock_user(mock_db_session, user_id)
    create_mock_organization(mock_db_session, org_id)
    create_mock_invitation(mock_db_session, user_id, org_id, id, datetime.now(timezone.utc), is_valid=True)
    
    response = client.delete(DELETE_INVITE_ENDPOINT.format(id=id))
    assert response.status_code == 401

if __name__ == "__main__":
    pytest.main()
