import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from unittest.mock import MagicMock, patch
from api.v1.models.user import User, Squeeze
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from fastapi import status

client = TestClient(app)
URI = "/api/v1/squeeze"
LOGIN_URI = "/api/v1/auth/login"

# Mock Data
squeeze1 = {
    "title": "My Squeeze Page",
    "email": "user1@example.com",
    "headline": "My Headline 1",
    "sub_headline": "My Sub Headline 1",
    "body": "My Body 1",
    "type": "product",
    "status": "offline",
    "user_id": str(uuid7()),
    "full_name": "My Full Name 1",
}
squeeze2 = {
    "title": "My Updated Squeeze Page",
    "email": "user1@example.com",
    "headline": "My Updated Headline",
    "sub_headline": "My Updated Sub Headline",
    "body": "My Updated Body",
    "type": "product",
    "status": "online",
    "user_id": str(uuid7()),
    "full_name": "My Updated Full Name",
}

# Mock User
def create_mock_super_admin(mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = User(
        id=str(uuid7()),
        email="user1@example.com",
        password=user_service.hash_password("P@ssw0rd"),
        is_super_admin=True,
    )

# Header with Authorization Token
theader = lambda token: {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_db_session():
    """Mock database session."""
    with patch("api.db.database.get_db") as mock_db:
        mock_session = MagicMock()
        mock_db.return_value = mock_session
        yield mock_session

def test_create_squeeze_page(mock_db_session):
    """Test create squeeze page."""
    create_mock_super_admin(mock_db_session)
    tok = client.post(
        LOGIN_URI, json={"email": "user1@example.com", "password": "P@ssw0rd"}
    ).json()
    assert tok["status_code"] == status.HTTP_200_OK
    token = tok["data"]["user"]["access_token"]
    res = client.post(URI, json=squeeze1, headers=theader(token))
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json()['data']['title'] == squeeze1["title"]
    assert res.json()['data']['email'] == squeeze1["email"]

@pytest.mark.parametrize("squeeze_id", [1, 2, 3])
def test_delete_squeeze_page(mock_db_session, squeeze_id):
    """Test delete squeeze page."""
    create_mock_super_admin(mock_db_session)
    mock_db_session.query.return_value.filter.return_value.first.return_value = Squeeze(id=squeeze_id)
    mock_db_session.query.return_value.filter.return_value.first.return_value = Squeeze(id=squeeze_id)
    tok = client.post(
        LOGIN_URI, json={"email": "user1@example.com", "password": "P@ssw0rd"}
    ).json()
    assert tok["status_code"] == status.HTTP_200_OK
    token = tok["data"]["user"]["access_token"]
    res = client.delete(f"{URI}/{squeeze_id}", headers=theader(token))
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["message"] == "Squeeze page deleted successfully!"

def test_edit_squeeze_page(mock_db_session):
    """Test edit squeeze page."""
    create_mock_super_admin(mock_db_session)
    mock_db_session.query.return_value.filter.return_value.first.return_value = Squeeze(id=1, **squeeze1)
    tok = client.post(
        LOGIN_URI, json={"email": "user1@example.com", "password": "P@ssw0rd"}
    ).json()
    assert tok["status_code"] == status.HTTP_200_OK
    token = tok["data"]["user"]["access_token"]
    res = client.put(f"{URI}/1", json=squeeze2, headers=theader(token))
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['data']['title'] == squeeze2["title"]
    assert res.json()['data']['email'] == squeeze2["email"]
