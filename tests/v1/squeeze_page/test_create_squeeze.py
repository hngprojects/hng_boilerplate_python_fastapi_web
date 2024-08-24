import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
from api.v1.models import User
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from fastapi import status
from api.db.database import get_db

client = TestClient(app)
URI = "/api/v1/squeeze"
LOGIN_URI = "api/v1/auth/login"

squeeze1 = {
    "title": "My Squeeze Page",
    "email": "user1@gmail.com",
    "headline": "My Headline 1",
    "sub_headline": "My Sub Headline 1",
    "body": "My Body 1",
    "type": "product",
    "status": "offline",
    "user_id": str(uuid7()),
    "full_name": "My Full Name 1",
    # expected response
    "status_code": 201,
}
squeeze2 = {
    "title": "My Squeeze Page",
    "email": "user1@gmail.com",
    "headline": "My Headline 2",
    "sub_headline": "My Sub Headline 2",
    "type": "product",
    "status": "online",
    "user_id": str(uuid7()),
    # expected response
    "status_code": 201,
}
squeeze3 = {
    "title": "My Squeeze Page",
    "email": "user2@gmail.com",
    "headline": "My Headline 3",
    "body": "My Body 3",
    "user_id": str(uuid7()),
    # expected response
    "status_code": 201,
}

# Mock the BackgroundTasks and email sending function
@pytest.fixture(scope='module')
def mock_send_email():
    with patch("api.core.dependencies.email_sender.send_email", return_value=None) as mock_email_sending:
        with patch("fastapi.BackgroundTasks.add_task") as add_task_mock:
            # Override the add_task method to simulate direct function call
            add_task_mock.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)
            yield mock_email_sending

@pytest.fixture
def mock_db_session(_=MagicMock()):
    """Mock session"""
    with patch(get_db.__module__):
        app.dependency_overrides[get_db] = lambda: _
        yield _
    app.dependency_overrides = {}


def create_mock_super_admin(_):
    """Mock super admin"""
    _.query.return_value.filter.return_value.first.return_value = User(
        id=str(uuid7()),
        email="user1@gmail.com",
        password=user_service.hash_password("P@ssw0rd"),
        is_superadmin=True,
    )


theader = lambda _: {"Authorization": f"Bearer {_}"}


@pytest.mark.parametrize("data", [squeeze1, squeeze2, squeeze3])
@pytest.mark.usefixtures("mock_db_session", "mock_send_email")
def test_create_squeeze_page(mock_db_session, data, mock_send_email):
    """Test create squeeze page."""
    create_mock_super_admin(mock_db_session)
    tok = client.post(
        LOGIN_URI, json={"email": "user1@gmail.com", "password": "P@ssw0rd"}
    ).json()
    print(tok)
    assert tok["status_code"] == status.HTTP_200_OK
    token = tok["access_token"]
    res = client.post(URI, json=data, headers=theader(token))
    assert res.status_code == data["status_code"]
    assert res.json()['data']['title'] == data["title"]
    assert res.json()['data']['email'] == data["email"]
