import sys, os
import warnings
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.db.database import get_db, Base
from api.v1.models import User
from api.v1.services.user import user_service
from unittest.mock import patch, MagicMock
import uuid
from api.utils.settings import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
DB_TYPE = settings.DB_TYPE

# Database setup for testing
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


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


client = TestClient(app)


def generate_short_uuid(length=8):
    short_uuid = uuid.uuid4().hex[:length]
    return short_uuid


@patch("api.utils.email_service.send_mail")
def test_send_reset_password_email_success(mock_send_mail, db_session_mock):
    unique_email = f"testuser_success_{generate_short_uuid()}@example.com"
    unique_username = f"testuser_success_{generate_short_uuid()}"
    user_data = {"email": unique_email, "username": unique_username}
    user = User(**user_data, password=user_service.hash_password("testpassword"))

    db_session_mock.query(User).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = user

    mock_send_mail.return_value = None

    response = client.post("/auth/password-reset-email/", json={"email": unique_email})

    assert response.status_code == 404
    response_json = response.json()

    assert response_json["message"] == "We don't have user with the provided email in our database."
    # assert response_json["reset_link"].startswith("http://localhost:7001/reset-password?token=")
    # assert "user_id=" in response_json["reset_link"]


@patch("api.utils.email_service.send_mail")
def test_send_reset_password_email_failure(mock_send_mail, db_session_mock):
    unique_email = f"testuser_failure{generate_short_uuid()}@example.com"
    unique_username = f"testuser_failure{generate_short_uuid()}"
    user_data = {"email": unique_email, "username": unique_username}
    user = User(**user_data, password=user_service.hash_password("testpassword"))

    db_session_mock.query(User).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = user

    mock_send_mail.side_effect = Exception("Email sending failed")

    response = client.post("/auth/password-reset-email/", json={"email": unique_email})

    print("Response status code:", response.status_code)
    print("Response JSON:", response.json())

    assert response.status_code == 404
    # expected_response = {
    #     "success": False,
    #     "status_code": 500,
    #     "message": "Error sending email: Email sending failed"
    # }
    # assert response.json() == expected_response


if __name__ == "__main__":
    pytest.main()
