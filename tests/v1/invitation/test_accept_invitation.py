import sys, os
import warnings
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from uuid_extensions import uuid7
from fastapi import status
from fastapi import HTTPException, Request
from urllib.parse import urlencode
from api.v1.models.permissions.role import Role
from api.v1.services.user import user_service
from api.v1.models.permissions.user_org_role import user_organisation_roles

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app
from api.v1.models.user import User
from api.v1.models.associations import user_organisation_association
from api.v1.models.invitation import Invitation
from api.v1.models.organisation import Organisation
from api.v1.services.invite import InviteService
from api.db.database import get_db

INVITE_CREATE_ENDPOINT = '/api/v1/invite/create'
INVITE_ACCEPT_ENDPOINT = '/api/v1/invite/accept'
LOGIN_ENDPOINT = 'api/v1/auth/login'

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    with patch("api.db.database.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


def create_mock_role(mock_db_session, role_name, role_id=None):
    mock_role = Role(
        id=role_id if role_id else uuid7(),
        name=role_name,
        is_builtin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query(Role).filter_by(name=role_name).first.return_value = mock_role
    return mock_role


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

def create_mock_role_assignment(mock_db_session, user_id, org_id, role_id):
    mock_db_session.query(user_organisation_roles).filter_by(
        user_id=user_id,
        organisation_id=org_id,
        role_id=role_id
    ).first.return_value = MagicMock()


def create_mock_organisation(mock_db_session, org_id):
    mock_org = Organisation(
        id=org_id,
        name="Test Organisation",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query(Organisation).filter_by(id=org_id).first.return_value = mock_org
    return mock_org


def create_mock_invitation(mock_db_session, user_id, org_id, invitation_id, expiration, is_valid):
    mock_invitation = Invitation(
        id=invitation_id,
        user_id=user_id,
        organisation_id=org_id,
        expires_at=expiration,
        is_valid=is_valid
    )
    mock_db_session.query(Invitation).filter_by(id=invitation_id, is_valid=True).first.return_value = mock_invitation
    return mock_invitation

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_create_invitation_valid_userid(mock_db_session, mock_invite_service):
    user_email = "mike@example.com"
    org_id = str(uuid7())

    create_mock_user(mock_db_session, user_email)
    create_mock_organisation(mock_db_session, org_id)

    access_token = user_service.create_access_token(str(user_email))
    mock_db_session.execute.return_value.fetchall.return_value = []

    paylod = {
        "user_email" : user_email,
        "organisation_id" : org_id
    }

    response = client.post(INVITE_CREATE_ENDPOINT, json=paylod, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json()['message'] == 'Invitation link created successfully'


@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_create_invitation_invalid_id(mock_db_session, mock_invite_service):
    user_id = 12345
    org_id = str(uuid7())
    
    create_mock_user(mock_db_session, user_id)
    create_mock_organisation(mock_db_session, org_id)

    access_token = user_service.create_access_token(str(user_id))
    mock_db_session.execute.return_value.fetchall.return_value = []

    paylod = {
        "user_id" : user_id,
        "organisation_id" : org_id
    }

    response = client.post(INVITE_CREATE_ENDPOINT, json=paylod, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 422
    assert response.json()['message'] == "Invalid input"

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_accept_invitation_expired_link(mock_db_session, mock_invite_service):
    """Test for accepting an expired invitation link."""
    user_id = str(uuid7())
    org_id = str(uuid7())
    invitation_id = str(uuid7())
    expiration = datetime.now(timezone.utc) - timedelta(days=1)
    access_token = user_service.create_access_token(str(user_id))
    create_mock_user(mock_db_session, user_id)
    create_mock_organisation(mock_db_session, org_id)
    create_mock_invitation(mock_db_session, user_id, org_id, invitation_id, expiration, is_valid=True)

    mock_invite_service.add_user_to_organisation.side_effect = HTTPException(status_code=400, detail="Expired invitation link")

    response = client.post(INVITE_ACCEPT_ENDPOINT, json={
        "invitation_link": f"http://testserver/api/v1/invite/accept?invitation_id={invitation_id}"
    }, headers={'Authorization': f'Bearer {access_token}'})

    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_accept_invitation_malformed_link(mock_db_session):
    """Test for accepting a malformed invitation link."""
    user_id = str(uuid7())
    org_id = str(uuid7())
    invitation_id = str(uuid7())
    expiration = datetime.now(timezone.utc) - timedelta(days=1)
    access_token = user_service.create_access_token(str(user_id))
    create_mock_user(mock_db_session, user_id)
    create_mock_organisation(mock_db_session, org_id)
    create_mock_invitation(mock_db_session, user_id, org_id, invitation_id, expiration, is_valid=True)
    response = client.post(INVITE_ACCEPT_ENDPOINT, json={
        "invitation_link": "http://testserver/api/v1/invite/accept?wrong_param=123"
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_accept_invitation_user_already_assigned(mock_db_session, mock_invite_service):
    """Test for accepting an invitation where the user is already assigned to the role in the organisation."""
    user_id = str(uuid7())
    org_id = str(uuid7())
    invitation_id = str(uuid7())
    expiration = datetime.now(timezone.utc) + timedelta(days=1)

    create_mock_user(mock_db_session, user_id)
    create_mock_organisation(mock_db_session, org_id)
    create_mock_invitation(mock_db_session, user_id, org_id, invitation_id, expiration, is_valid=True)
    
    # Simulate the scenario where the user is already assigned to the organisation
    mock_invite_service.add_user_to_organisation.side_effect = HTTPException(
        status_code=400, 
        detail="User is already assigned to the role in this organisation"
    )
    
    access_token = user_service.create_access_token(str(user_id))
    mock_db_session.execute.return_value.fetchall.return_value = []

    response = client.post(INVITE_ACCEPT_ENDPOINT, json={
        "invitation_link": f"http://testserver/api/v1/invite/accept?invitation_id={invitation_id}"
    }, headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 400
    assert response.json()['message'] == 'User is already assigned to the role in this organisation'
