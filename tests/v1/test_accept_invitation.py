import sys, os
import warnings
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from uuid_extensions import uuid7
from fastapi import status
from fastapi import HTTPException

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app
from api.v1.models.user import User
from api.v1.models.invitation import Invitation
from api.v1.models.org import Organization
from api.v1.services.invite import InviteService
from api.db.database import get_db


INVITE_CREATE_ENDPOINT = '/api/v1/invite/create'
INVITE_ACCEPT_ENDPOINT = '/api/v1/invite/accept'

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    with patch("api.v1.services.invite.get_db", autospec=True) as mock_get_db:
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
        username="testuser",
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
def test_accept_invitation_valid_link(mock_db_session, mock_invite_service):
    user_id = str(uuid7())
    org_id = str(uuid7())
    invitation_id = str(uuid7())
    expiration = datetime.now(timezone.utc) + timedelta(days=1)

    create_mock_user(mock_db_session, user_id)
    create_mock_organization(mock_db_session, org_id)
    create_mock_invitation(mock_db_session, user_id, org_id, invitation_id, expiration, is_valid=True)

    mock_db_session.execute.return_value.fetchall.return_value = []

    response = client.post(INVITE_ACCEPT_ENDPOINT, json={
        "invitation_link": f"http://testserver/api/v1/invite/accept?invitation_id={invitation_id}"
    })

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "User added to organization successfully"
    }
    #mock_invite_service.add_user_to_organization.assert_called_once_with(invitation_id, mock_db_session)


@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_accept_invitation_expired_link(mock_db_session, mock_invite_service):
    """Test for accepting an expired invitation link."""
    user_id = str(uuid7())
    org_id = str(uuid7())
    invitation_id = str(uuid7())
    expiration = datetime.now(timezone.utc) - timedelta(days=1)

    create_mock_user(mock_db_session, user_id)
    create_mock_organization(mock_db_session, org_id)
    create_mock_invitation(mock_db_session, user_id, org_id, invitation_id, expiration, is_valid=True)

    mock_invite_service.add_user_to_organization.side_effect = HTTPException(status_code=400, detail="Expired invitation link")

    response = client.post(INVITE_ACCEPT_ENDPOINT, json={
        "invitation_link": f"http://testserver/api/v1/invite/accept?invitation_id={invitation_id}"
    })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'success': False, 'status_code': 400, 'message': 'Expired invitation link'}
    #mock_invite_service.add_user_to_organization.assert_called_once_with(invitation_id, mock_db_session)

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_accept_invitation_malformed_link(mock_db_session):
    """Test for accepting a malformed invitation link."""
    response = client.post(INVITE_ACCEPT_ENDPOINT, json={
        "invitation_link": "http://testserver/api/v1/invite/accept?wrong_param=123"
    })

    print(response.json())
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'success': False, 'status_code': 400, 'message': 'Invalid invitation link'}


@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_load_testing(mock_db_session, mock_invite_service):
    """Perform load testing to ensure the endpoint can handle multiple requests."""
    user_id = str(uuid7())
    org_id = str(uuid7())
    invitation_id = str(uuid7())
    expiration = datetime.now(timezone.utc) + timedelta(days=1)

    create_mock_user(mock_db_session, user_id)
    create_mock_organization(mock_db_session, org_id)
    create_mock_invitation(mock_db_session, user_id, org_id, invitation_id, expiration, is_valid=True)


    mock_db_session.execute.return_value.fetchall.return_value = []
    responses = []
    for _ in range(100):  # Simulate 100 concurrent requests
        response = client.post(INVITE_ACCEPT_ENDPOINT, json={
            "invitation_link": f"http://testserver/api/v1/invite/accept?invitation_id={invitation_id}"
        })
        responses.append(response)

    success_count = sum(1 for r in responses if r.status_code == 200)

    assert success_count == 100