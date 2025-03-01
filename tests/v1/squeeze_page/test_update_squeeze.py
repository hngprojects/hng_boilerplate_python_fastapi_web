from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.squeeze import Squeeze
from api.v1.models.user import User
from api.v1.schemas.squeeze import UpdateSqueeze
from api.v1.services.user import user_service
from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db_session():
    db = MagicMock(spec=Session)
    yield db


@pytest.fixture
def mock_user():
    return User(
        id=f"{uuid7()}",
        email="test@example.com",
        password="hashedpassword1",
        first_name="test",
        last_name="user",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture()
def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def valid_squeeze():
    return UpdateSqueeze(
        title="Updated Squeeze Page", headline="This is the new headline"
    )


@pytest.fixture
def exisiting_squeeze(mock_db_session):
    squeeze = Squeeze(
        id=str(uuid7()),
        title="My Squeeze Page",
        email="user1@example.com",
        headline="My Headline 1",
        sub_headline="My Sub Headline 1",
        body="My Body 1",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db_session.query(Squeeze).filter(
        Squeeze.id == squeeze.id
    ).first.return_value = squeeze
    return squeeze


def test_update_squeeze_success(
    client, mock_db_session, exisiting_squeeze, valid_squeeze, mock_get_current_admin
):
    """Test to successfully update a squeeze page"""

    # Mock the dependencies
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[user_service.get_current_super_admin] = (
        lambda: mock_get_current_admin
    )

    response = client.put(
        f"api/v1/squeeze/{exisiting_squeeze.id}",
        headers={"Authorization": "Bearer token"},
        json=valid_squeeze.model_dump(),
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["data"]["title"] == valid_squeeze.title
    assert response_data["data"]["headline"] == valid_squeeze.headline


def test_update_squeeze_not_found(
    client, mock_db_session, valid_squeeze, mock_get_current_admin
):
    """Test updating a non-existent squeeze page"""

    non_existent_id = str(uuid7())
    mock_db_session.query(Squeeze).filter(
        Squeeze.id == non_existent_id
    ).first.return_value = None

    # Mock the dependencies
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[user_service.get_current_super_admin] = (
        lambda: mock_get_current_admin
    )

    response = client.put(
        f"api/v1/squeeze/{non_existent_id}",
        headers={"Authorization": "Bearer token"},
        json=valid_squeeze.model_dump(),
    )

    assert response.status_code == 404


def test_update_squeeze_internal_error(
    client, mock_db_session, exisiting_squeeze, valid_squeeze, mock_get_current_admin
):
    """Test for internal server error during update"""

    # Simulate a database error
    mock_db_session.commit.side_effect = Exception("Database error")

    # Mock the dependencies
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[user_service.get_current_super_admin] = (
        lambda: mock_get_current_admin
    )

    response = client.put(
        f"api/v1/squeeze/{exisiting_squeeze.id}",
        headers={"Authorization": "Bearer token"},
        json=valid_squeeze.model_dump(),
    )

    assert response.status_code == 500
