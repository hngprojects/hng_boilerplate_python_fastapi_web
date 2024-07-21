import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import uuid
from api.db.database import Base, get_db, SessionLocal
# from api.v1.services.email.waitlist_email import send_confirmation_email

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db(mocker):
    mock_engine = MagicMock()  # Mock the database engine
    mocker.patch('api.db.database.get_db_engine', return_value=mock_engine)

    mock_create_all = mocker.patch(
        'api.db.database.Base.metadata.create_all', autospec=True)
    mock_drop_all = mocker.patch(
        'api.db.database.Base.metadata.drop_all', autospec=True)

    mock_create_all.return_value = None
    mock_drop_all.return_value = None

    session = MagicMock()
    mocker.patch('api.db.database.SessionLocal', return_value=session)

    yield session

    mock_create_all.assert_called_once_with(bind=mock_engine)
    mock_drop_all.assert_called_once_with(bind=mock_engine)


@pytest.fixture(scope="function")
def client_with_mocks(test_db):
    with patch('api.db.database.get_db', return_value=test_db):
        yield client


# @pytest.fixture(scope="function", autouse=True)
# def mock_email_config(mocker):
#     mocker.patch(
#         'api.v1.services.email.waitlist_email.ConnectionConfig', autospec=True)
#     mocker.patch('api.v1.services.email.waitlist_email.FastMail', autospec=True)
#     mock_send_message = mocker.patch(
#         'api.v1.services.email.waitlist_email.FastMail.send_message', autospec=True)
#     yield mock_send_message


def test_signup_waitlist(client_with_mocks, mock_email_config, mocker):
    # Mock rate_limit decorator
    mocker.patch('api.utils.rate_limiter.rate_limit', return_value=MagicMock())

    email = f"test{uuid.uuid4()}@example.com"

    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": email, "full_name": "Test User"}
    )

    assert response.status_code == 201
    assert response.json() == {"message": "You are all signed up!"}


# def test_send_confirmation_email(mocker):

#     mock_mail = MagicMock()
#     mocker.patch('api.v1.services.email.waitlist_email.FastMail', return_value=mock_mail)


#     email = "test@example.com"
#     full_name = "Test User"
#     mocker.patch('api.v1.services.email.waitlist_email.send_confirmation_email', autospec=True)

#     mock_mail.send_message = MagicMock()
#     await send_confirmation_email(email, full_name)


#     mock_mail.send_message.assert_called_once()


def test_duplicate_email(client_with_mocks):
    client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "duplicate@example.com", "full_name": "Test User"}
    )
    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "duplicate@example.com", "full_name": "Another User"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_invalid_email(client_with_mocks):
    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "invalid_email", "full_name": "Test User"}
    )
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()[
        "detail"][0]["msg"]


def test_signup_with_empty_name(client_with_mocks):
    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "test@example.com", "full_name": ""}
    )
    assert response.status_code == 422
    assert "Full name is required" in response.json().get("detail", "")


def test_rate_limiting(client_with_mocks, mocker):
    # Mock rate_limit decorator
    mocker.patch('api.utils.rate_limiter.rate_limit', return_value=MagicMock())

    for _ in range(5):
        client_with_mocks.post(
            "/api/v1/waitlist",
            json={"email": f"test{_}@example.com", "full_name": "Test User"}
        )

    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": "toomany@example.com", "full_name": "Test User"}
    )
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]
