import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from api.v1.models.data_privacy import DataPrivacySetting
from api.v1.models.user import User
from main import app
from api.v1.routes.blog import get_db
from api.v1.services.user import user_service


# Mock database dependency
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


# Mock user service dependency

user_id = uuid7()
dp_setting_id = uuid7()
timezone_offset = -8.0
tzinfo = timezone(timedelta(hours=timezone_offset))
timeinfo = datetime.now(tzinfo)
created_at = timeinfo
updated_at = timeinfo
access_token = user_service.create_access_token(str(user_id))
access_token2 = user_service.create_access_token(str(uuid7()))

# create test user

user = User(
    id=str(user_id),
    email="testuser@test.com",
    password="password123",
    created_at=created_at,
    updated_at=updated_at,
)

# create test data privacy

data_privacy = DataPrivacySetting(
    id=dp_setting_id,
    user_id=user_id,
)

user.data_privacy_setting = data_privacy


def test_update_data_privacy_success(client, db_session_mock):
    db_session_mock.query().filter().all.first.return_value = data_privacy
    headers = {"authorization": f"Bearer {access_token}"}

    data = {"receice_email_updates": False, "personalized_ads": True}

    response = client.patch(
        f"/api/v1/settings/data-privacy", headers=headers, json=data
    )

    assert response.status_code == 200


def test_update_data_privacy_invalid_data(client, db_session_mock):
    db_session_mock.query().filter().all.first.return_value = data_privacy
    headers = {"authorization": f"Bearer {access_token}"}

    response = client.patch(f"/api/v1/settings/data-privacy", headers=headers)

    assert response.status_code == 422


def test_update_data_privacy_unauthenticated_user(client):
    response = client.patch(f"/api/v1/settings/data-privacy")

    assert response.status_code == 401
