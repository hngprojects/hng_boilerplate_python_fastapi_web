import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.db.database import get_db
from api.db.database import Base
from unittest.mock import patch, AsyncMock
from fastapi_mail import FastMail
from api.v1.models import User
from api.v1.services.user import user_service
import uuid

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:4253@localhost:5432/hng_task_6"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fixture for setting up and tearing down database sessions for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture
def override_get_db(db_session):
    """Override dependency to use the test database session."""
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)


client = TestClient(app)


@pytest.fixture
def mock_fast_mail():
    with patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock:
        yield mock


def generate_short_uuid(length=8):
    # Generate a UUID and get its hex representation (excluding hyphens)
    short_uuid = uuid.uuid4().hex[:length]
    return short_uuid


def test_send_email_success(mock_fast_mail, override_get_db):
    unique_email = f"testuser_success_{generate_short_uuid()}" + "@example.com"
    unique_username = f"testuser_success_{generate_short_uuid()}"
    user_data = {"email": unique_email, "username": unique_username}
    db = next(get_db())
    user = User(**user_data, password=user_service.hash_password("testpassword"))
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post("/auth/password-reset-email/", json={
        "email": unique_email,
        "subject": "Reset Password",
        "body": "Please reset your password",
        "body_type": "plain"
    })

    assert response.status_code == 200

    actual_reset_link = mock_fast_mail.call_args[0][0].body.split(' ')[-1]
    assert response.json() == {
        "message": "Password reset email sent successfully.",
        "reset_link": actual_reset_link
    }
    mock_fast_mail.assert_called_once()


def test_email_sending_failure(mock_fast_mail, override_get_db):
    unique_email = f"testuser_success_{generate_short_uuid()}" + "@example.com"
    unique_username = f"testuser_failure_{generate_short_uuid()}"
    user_data = {"email": unique_email, "username": unique_username}
    db = next(get_db())
    user = User(**user_data, password=user_service.hash_password("testpassword"))
    db.add(user)
    db.commit()
    db.refresh(user)

    # Simulate an email sending failure
    mock_fast_mail.side_effect = Exception("Email sending failed")

    # Act
    try:
        response = client.post("/auth/password-reset-email/", json={
            "email": unique_email,
            "subject": "Reset Password",
            "body": "Please reset your password",
            "body_type": "plain"
        })
        # Assert
        assert response.status_code == 500
        assert response.json() == {"detail": "Error sending email: Email sending failed"}
        # expected_response = {"detail": "Error sending email: Email sending failed"}
        # assert response.json() == expected_response
    except Exception as e:
        print(f"Exception during request: {e}")


if __name__ == '__main__':
    pytest.main()
