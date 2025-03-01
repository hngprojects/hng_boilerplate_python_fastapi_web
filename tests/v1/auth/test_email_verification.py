import uuid
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from main import app
from api.db.database import Base, engine
from api.v1.models import User
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from jose import jwt
from api.utils.settings import settings
import uuid

# Set up a test database session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def client():
    """Fixture to provide a test client for the API."""
    Base.metadata.create_all(bind=engine)
    test_client = TestClient(app)
    yield test_client

@pytest.fixture(scope="function")
def db_session():
    """Fixture to provide a fresh database session for each test."""
    db = TestingSessionLocal()
    yield db
    db.close()



def create_test_user(db_session, email=None, verified=False):
    """Helper function to create a test user with a unique email."""
    if email is None:
        email = f"testuser_{uuid.uuid4().hex[:8]}@gmail.com"  # Generate inside function

    user = User(
        email=email,
        password="Jeffmaine240@", 
        first_name="jeff", 
        last_name="last", 
        is_verified=verified
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def generate_token(user_id, expired=False):
    """Helper function to generate a JWT token."""
    # expiry_time = datetime.now() + timedelta(seconds=exp)
    # exp_timestamp = int(expiry_time.timestamp())
    exp_time = int((datetime.now() + (timedelta(minutes=-1) if expired else timedelta(minutes=30))).timestamp())
    return jwt.encode({"sub": user_id, "exp": exp_time}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# @patch("api.core.dependencies.email_sender.send_email")
# def test_resend_verification_email(mock_send_email, client:TestClient, db_session):
#     """Test resending verification email."""
#     user = create_test_user(db_session)
#     response = client.post("/api/v1/auth/resend_verification_email", json={"email": user.email})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert data["message"] == "Verification email sent successfully"
    # print(mock_send_email.call_args_list)



def test_verify_email_valid_token(client: TestClient, db_session):
    """Test email verification with a valid token."""
    user = create_test_user(db_session)
    token = generate_token(user.id)
    response = client.get(f"/api/v1/auth/verify-email?token={token}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Email verified successfully."


def test_verify_email_expired_token(client: TestClient, db_session):
    """Test email verification with an expired token."""
    user = create_test_user(db_session)
    token = generate_token(user.id, expired=True)
    response = client.get(f"/api/v1/auth/verify-email?token={token}")
    assert response.status_code == 400
    data = response.json()
    assert data["status"] is False
    assert data["message"] == "Verification link expired"


def test_verify_email_invalid_token(client:TestClient):
    """Test email verification with an invalid token."""
    response = client.get("/api/v1/auth/verify-email?token=invalidtoken")
    assert response.status_code == 400
    data = response.json()
    print(data)
    assert data["message"] == "Invalid token"