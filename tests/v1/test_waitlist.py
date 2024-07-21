import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import uuid
from api.db.database import Base, get_db, SessionLocal

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db(mocker):
    # Mock the database engine
    mock_engine = MagicMock()
    mocker.patch('api.db.database.get_db_engine', return_value=mock_engine)

    # Mock the database creation and teardown
    mock_create_all = mocker.patch(
        'api.db.database.Base.metadata.create_all', autospec=True)
    mock_drop_all = mocker.patch(
        'api.db.database.Base.metadata.drop_all', autospec=True)

    mock_create_all.return_value = None
    mock_drop_all.return_value = None

    # Create a session instance
    session = MagicMock()
    mocker.patch('api.db.database.SessionLocal', return_value=session)

    yield session

    # Ensure create_all and drop_all were called
    mock_create_all.assert_called_once_with(bind=mock_engine)
    mock_drop_all.assert_called_once_with(bind=mock_engine)


@pytest.fixture(scope="function")
def client_with_mocks(test_db):
    with patch('api.db.database.get_db', return_value=test_db):
        yield client

# Mock email configuration


@pytest.fixture(scope="function", autouse=True)
def mock_email_config(mocker):
    mocker.patch(
        'api.v1.services.waitlist_email.ConnectionConfig', autospec=True)


def test_signup_waitlist(client_with_mocks, mocker):
    # Mock the rate limiting logic if needed
    mocker.patch('api.v1.routes.waitlist.rate_limit', return_value=MagicMock())

    # Use a unique email address for each test
    email = f"test{uuid.uuid4()}@example.com"

    response = client_with_mocks.post(
        "/api/v1/waitlist",
        json={"email": email, "full_name": "Test User"}
    )

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")

    assert response.status_code == 201
    assert response.json() == {"message": "You are all signed up!"}


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
    assert "Full name is required" in response.json()["detail"][0]["msg"]


def test_rate_limiting(client_with_mocks, mocker):
    # Mock the rate limiting logic if needed
    mocker.patch('api.v1.routes.waitlist.rate_limit', return_value=MagicMock())

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
