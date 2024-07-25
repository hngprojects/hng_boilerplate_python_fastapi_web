import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.db.database import get_db, Base
from api.v1.models import User
from api.v1.services.user import user_service
from unittest.mock import patch
import uuid

# Database setup for testing
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

def generate_short_uuid(length=8):
    """Generate a short UUID."""
    short_uuid = uuid.uuid4().hex[:length]
    return short_uuid

@patch("api.utils.email_service.send_mail")
def test_send_reset_password_email_success(mock_send_mail, override_get_db):
    unique_email = f"testuser_success_{generate_short_uuid()}@example.com"
    unique_username = f"testuser_success_{generate_short_uuid()}"
    user_data = {"email": unique_email, "username": unique_username}
    db = next(get_db())
    user = User(**user_data, password=user_service.hash_password("testpassword"))
    db.add(user)
    db.commit()
    db.refresh(user)

    # Mock the send_mail function
    mock_send_mail.return_value = None

    response = client.post("/auth/password-reset-email/", json={"email": unique_email})

    assert response.status_code == 200
    response_json = response.json()

    # Check the response message and partially validate the reset_link
    assert response_json["message"] == "Password reset email sent successfully."
    assert response_json["reset_link"].startswith("http://localhost:7001/reset-password?token=")
    assert "user_id=" in response_json["reset_link"]

@patch("api.utils.email_service.send_mail")
def test_send_reset_password_email_failure(mock_send_mail, override_get_db):
    unique_email = f"testuser_failure{generate_short_uuid()}@example.com"
    unique_username = f"testuser_failure{generate_short_uuid()}"
    user_data = {"email": unique_email, "username": unique_username}
    db = next(get_db())
    user = User(**user_data, password=user_service.hash_password("testpassword"))
    db.add(user)
    db.commit()
    db.refresh(user)

    # Simulate an email sending failure
    mock_send_mail.side_effect = Exception("Email sending failed")

    response = client.post("/auth/password-reset-email/", json={"email": unique_email})

    print("Response status code:", response.status_code)
    print("Response JSON:", response.json())

    assert response.status_code != 500
    assert response.json() != {"detail": "Error sending email: Email sending failed"}