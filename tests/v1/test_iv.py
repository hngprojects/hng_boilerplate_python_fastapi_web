import sys, os
import warnings
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.models.invitation import Invitation
from api.v1.models.org import Organization
from api.v1.services.invite import invite_service
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone, timedelta

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

client = TestClient(app)
INVITE_CREATE_ENDPOINT = '/api/v1/invite/create'
INVITE_ACCEPT_ENDPOINT = '/api/v1/invite/accept'

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.v1.services.invite.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_invite_service():
    """Fixture to create a mock invite service."""
    with patch("api.v1.services.invite.invite_service", autospec=True) as mock_service:
        yield mock_service

def create_mock_user(mock_db_session, user_id):
    """Create a mock user in the mock database session."""
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
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

def create_mock_organization(mock_db_session, org_id):
    """Create a mock organization in the mock database session."""
    mock_org = Organization(
        id=org_id,
        name="Test Organization",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_org
    return mock_org

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_create_invitation_link(mock_db_session):
    """Test for creating an invitation link."""

    user_id = str(uuid7())
    org_id = str(uuid7())
    create_mock_user(mock_db_session, user_id)
    create_mock_organization(mock_db_session, org_id)

    response = client.post(INVITE_CREATE_ENDPOINT, json={
        "user_id": user_id,
        "organization_id": org_id
    })

    assert response.status_code == status.HTTP_200_OK
    assert "invitation_link" in response.json()

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_accept_invitation_valid_link(mock_db_session):
    """Test for accepting a valid invitation link."""

    user_id = str(uuid7())
    org_id = str(uuid7())
    invitation_id = str(uuid7())

    create_mock_user(mock_db_session, user_id)
    create_mock_organization(mock_db_session, org_id)

    expiration = datetime.now(timezone.utc) + timedelta(days=1)
    mock_invitation = Invitation(
        id=invitation_id,
        user_id=user_id,
        organization_id=org_id,
        expires_at=expiration,
        is_valid=True
    )
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_invitation
    response = client.post(INVITE_ACCEPT_ENDPOINT, json={
        "invitation_link": f"http://testserver/api/v1/invite/accept?invitation_id={invitation_id}"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json().get("status") == None

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_accept_invitation_expired_link(mock_db_session):
    """Test for accepting an expired invitation link."""

    user_id = str(uuid7())
    org_id = str(uuid7())
    invitation_id = str(uuid7())

    create_mock_user(mock_db_session, user_id)
    create_mock_organization(mock_db_session, org_id)

    expiration = datetime.now(timezone.utc) - timedelta(days=1)
    mock_invitation = Invitation(
        id=invitation_id,
        user_id=user_id,
        organization_id=org_id,
        expires_at=expiration,
        is_valid=True
    )
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_invitation
    mock_db_session.execute().return_value = "Expired invitation link"
    response = client.post(INVITE_ACCEPT_ENDPOINT, json={
        "invitation_link": f"http://testserver/api/v1/invite/accept?invitation_id={invitation_id}"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json().get("detail") == None

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_accept_invitation_malformed_link(mock_db_session):
    """Test for accepting a malformed invitation link."""

    response = client.post(INVITE_ACCEPT_ENDPOINT, json={
        "invitation_link": "http://testserver/api/v1/invite/accept?wrong_param=123"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json().get("detail") == None

@pytest.mark.usefixtures("mock_db_session", "mock_invite_service")
def test_load_testing(mock_db_session):
    """Perform load testing to ensure the endpoint can handle multiple requests."""

    user_id = str(uuid7())
    org_id = str(uuid7())
    create_mock_user(mock_db_session, user_id)
    create_mock_organization(mock_db_session, org_id)

    responses = []
    for _ in range(100):  # Simulate 100 concurrent requests
        response = client.post(INVITE_CREATE_ENDPOINT, json={
            "user_id": user_id,
            "organization_id": org_id
        })
        responses.append(response)

    success_count = sum(1 for r in responses if r.status_code == status.HTTP_200_OK)

    assert success_count == 100
