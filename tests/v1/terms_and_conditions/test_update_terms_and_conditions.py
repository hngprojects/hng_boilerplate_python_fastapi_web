import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from unittest.mock import MagicMock, patch
from api.v1.models import *
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from fastapi import status

client = TestClient(app)
URI = "/api/v1/terms-and-conditions"
LOGIN_URI = "api/v1/auth/login"

test_old_data = {
    "title": "My Terms and Conditions",
    "content": "My Content",
}

test_new_data = {
    "title": "My New Terms and Conditions",
    "content": "My New Content",
}


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
        email="user@gmail.com",
        password=user_service.hash_password("P@ssw0rd"),
        is_superadmin=True,
    )

def create_mock_terms_and_conditions(_):
    """Mock terms and conditions"""
    _.query.return_value.filter.return_value.first.return_value = TermsAndConditions(
        id=str(uuid7()),
        title=test_old_data["title"],
        content=test_old_data["content"],
    )


theader = lambda _: {"Authorization": f"Bearer {_}"}


@pytest.mark.parametrize("data", [test_new_data])
@pytest.mark.usefixtures("mock_db_session")
def test_update_terms_and_conditions(mock_db_session, data):
    """Test update terms and conditions"""
    status_code = status.HTTP_200_OK
    create_mock_super_admin(mock_db_session)
    tok = client.post(
        LOGIN_URI, json={"email": "user@gmail.com", "password": "P@ssw0rd"}
    ).json()
    assert tok["status_code"] == status.HTTP_200_OK
    token = tok["access_token"]
    res = client.patch(f"{URI}/123", json=data, headers=theader(token))
    assert res.status_code == status_code
