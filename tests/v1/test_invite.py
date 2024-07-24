import sys
import os
import warnings
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.invitation import Invitation
from api.db.database import get_db
from urllib.parse import urlencode
from uuid_extensions import uuid7
from fastapi import status
from datetime import datetime, timedelta
from pytz import utc

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}

@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""
    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service

def test_accept_invite_valid_link(mock_user_service, mock_db_session):
    # Create test data
    user = User(id=str(uuid7()), email="testuser@example.com", username="testuser1234", password="password")
    org = Organization(id=str(uuid7()), name="Test Organization")
    mock_db_session.add(user)
    mock_db_session.add(org)
    mock_db_session.commit()  # Commit user and organization before adding invitation

    # Set the datetime directly without mocking
    expires_at = datetime.utcnow() + timedelta(days=1)
    invitation = Invitation(
        id=str(uuid7()),  # Generate a new UUID for the invitation
        user_id=user.id,
        organization_id=org.id,
        expires_at=expires_at,
        is_valid=True
    )
    mock_db_session.add(invitation)
    mock_db_session.commit()  # Commit invitation

    base_url = client.base_url
    invite_link = f'{base_url}api/v1/invite/accept?{urlencode({"invitation_id": str(invitation.id)})}'

    response = client.post(
        "/api/v1/invite/accept",
        json={"invitation_link": invite_link}
    )
    
    print("Invite Link:", invite_link)
    print("JSON Response:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "User added to organization successfully"

    # Debug invitation details from the database
    invite_from_db = mock_db_session.query(Invitation).filter_by(id=invitation.id).first()
    print(f"Invitation from DB: {invite_from_db}")
    print(f"Invitation ID: {invite_from_db.id}")
    print(f"Invitation User ID: {invite_from_db.user_id}")
    print(f"Invitation Organization ID: {invite_from_db.organization_id}")
    print(f"Invitation Expires At: {invite_from_db.expires_at}")
    print(f"Invitation Is Valid: {invite_from_db.is_valid}")
