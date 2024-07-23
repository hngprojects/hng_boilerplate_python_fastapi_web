import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.models.blog import Blog
from unittest.mock import MagicMock
import uuid
from api.db.database import get_db
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.v1.models.user import User


client = TestClient(app)

# you can follow this format for other tests, to mock the database


# step 1
# Mock the database dependency
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session


# step 2
# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = get_db_override


# step 3
# Mock the user_service.get_current_user
# this step eliminates the need to manually send a login request for each test that requires auth
@pytest.fixture()
def override_get_current_user():
    app.dependency_overrides[user_service.get_current_user] = lambda: User(
        username="testuser",
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_admin=False,
    )


# step 3.5
# Mock the user_service.get_current_user for inactive user
# you can create different kinds of users like this
@pytest.fixture()
def override_get_current_user_inactive():
    app.dependency_overrides[user_service.get_current_user] = lambda: User(
        username="testuser1",
        email="testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=False,
        is_admin=False,
    )


# Test unauthorized access to endpoint


def test_user_deactivation_unauthorized(db_session_mock: Session):
    unauthorized = client.post(
        "/api/v1/users/deactivation",
        json={"reason": "No longer need the account", "confirmation": True},
    )
    assert unauthorized.status_code == 401


# Test authorized access by active user

# Test for error


def test_error_user_deactivation(db_session_mock: Session, override_get_current_user):
    """Test for user deactivation"""

    missing_field = client.post(
        "/api/v1/users/deactivation",
        json={"reason": "No longer need the account"},
    )
    assert missing_field.status_code == 422

    # confirmation_false = client.post(
    #     "/api/v1/users/deactivation",
    #     json={"reason": "No longer need the account", "confirmation": False},
    # )

    # print(confirmation_false.json())

    # assert confirmation_false.status_code == 400
    # assert (
    #     confirmation_false.json()["message"]
    #     == "Confirmation required to deactivate account"
    # )


# Test for successfull deactivation


def test_success_deactivation(db_session_mock: Session, override_get_current_user):
    success_deactivation = client.post(
        "/api/v1/users/deactivation",
        json={"reason": "No longer need the account", "confirmation": True},
    )

    assert success_deactivation.status_code == 200


# Test for access by inactive user


def test_user_inactive(db_session_mock: Session, override_get_current_user_inactive):
    user_already_deactivated = client.post(
        "/api/v1/users/deactivation",
        json={"reason": "No longer need the account", "confirmation": True},
    )

    assert user_already_deactivated.status_code == 403
    assert user_already_deactivated.json()["message"] == "User is not active"
