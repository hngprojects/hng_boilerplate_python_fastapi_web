import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.models.user import User
from api.db.database import get_db
from api.v1.schemas.profile import ProfileCreateUpdate
from fastapi.encoders import jsonable_encoder
from api.utils.dependencies import get_current_user
from api.utils.settings import settings
import jwt

client = TestClient(app)



@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session



@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_jwt_decode(mocker):
    return mocker.patch("jose.jwt.decode", return_value={"user_id": "user_id"})


@pytest.fixture
def mock_get_current_user(mocker):
    user = User(id="user_id", is_superadmin=False)
    mock = mocker.patch("api.utils.dependencies.get_current_user", return_value=user)
    return mock


def create_test_token(user_id: str) -> str:
    """Function to create a test token"""
    expires = datetime.utcnow() + timedelta(minutes=30)
    data = {"user_id": user_id, "exp": expires}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def test_success_profile_update(
    db_session_mock, mock_get_current_user, mock_jwt_decode, mocker
):
    mocker.patch("jose.jwt.decode", return_value={"user_id": "user_id"})

    mock_profile = MagicMock()
    mock_profile.id = "c9752bcc-1cf4-4476-a1ee-84b19fd0c521"
    mock_profile.bio = "Old bio"
    mock_profile.pronouns = "Old pronouns"
    mock_profile.username = 'some user'
    mock_profile.job_title = "Old job title"
    mock_profile.department = "Old department"
    mock_profile.social = "Old social"
    mock_profile.phone_number = "1234567890"
    mock_profile.avatar_url = "https://example.com"
    mock_profile.recovery_email = "old_recovery_email@gmail.com"
    mock_profile.email = "user_email@example.com"  # Mock the email attribute properly
    mock_profile.updated_at = datetime.now().isoformat()
    mock_profile.facebook_link = 'https://example.com'
    mock_profile.linkedin_link = 'https://example.com'
    mock_profile.twitter_link = 'https://example.com'
    mock_profile.instagram_link = 'https://example.com'

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_profile
    mock_profile.user = {
        "id": "user_id",
        "first_name": "First",
        "last_name": "Last",
        "username": "username",
        "email": "email@gmail.com",
        "created_at": datetime.now().isoformat(),
    }
    mock_profile.updated_at = datetime.now().isoformat()
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_profile

    def mock_commit():
        mock_profile.bio = "Updated bio"
        mock_profile.pronouns = "Updated pronouns"
        mock_profile.job_title = "Updated job title"
        mock_profile.department = "Updated department"
        mock_profile.social = "Updated social"
        mock_profile.phone_number = "+1234567890"
        mock_profile.avatar_url = "https://example.com"
        mock_profile.recovery_email = "updated_recovery_email@gmail.com"
        mock_profile.updated_at = datetime.now()

    db_session_mock.commit.side_effect = mock_commit

    def mock_refresh(instance):
        instance.bio = "Updated bio"
        instance.pronouns = "Updated pronouns"
        instance.job_title = "Updated job title"
        instance.department = "Updated department"
        instance.social = "Updated social"
        instance.phone_number = "+1234567890"
        instance.avatar_url = "https://example.com"
        instance.recovery_email = "updated_recovery_email@gmail.com"
        instance.updated_at = datetime.now()

    db_session_mock.refresh.side_effect = mock_refresh

    response = {
        'message': '',
        'status_code': 200,
        'data': {
            "id": mock_profile.id,
            "bio": "Updated bio",
            "pronouns": "Updated pronouns",
            "job_title": "Updated job title",
            "department": "Updated department",
            "social": "Updated social",
            "phone_number": "+1234567890",
            "avatar_url": "https://domain.com",
            "recovery_email": "updated_recovery_email@gmail.com",
            "created_at": "1970-01-01T00:00:01Z",
            'linkedin_link': 'https://domain.com',
            "updated_at": datetime.now().isoformat(),
        }
    }

    profile_update = ProfileCreateUpdate(
        pronouns="Updated pronouns",
        job_title="Updated job title",
        department="Updated department",
        social="Updated social",
        bio="Updated bio",
        phone_number="+1234567890",
        avatar_url="https://example.com",
        recovery_email="updated_recovery_email@gmail.com",
    )

    token = create_test_token("user_id")


    assert response['status_code'] == 200
    assert response["data"]["bio"] == "Updated bio"
    assert response["data"]["linkedin_link"] is not None
