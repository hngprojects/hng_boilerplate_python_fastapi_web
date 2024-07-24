import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from decouple import config
from uuid_extensions import uuid7
from main import app
from api.db.database import Base, get_db
from datetime import datetime, timedelta
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.invitation import Invitation
import uuid

#DB for test
SQLALCHEMY_DATABASE_URL = config('DB_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()
    # Cleanup after each test
    db = TestingSessionLocal()
    db.execute(text("TRUNCATE TABLE invitations RESTART IDENTITY CASCADE"))
    db.execute(text("TRUNCATE TABLE organizations RESTART IDENTITY CASCADE"))
    db.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    db.commit()

def test_accept_invite_valid_link(test_db):
    # Create test data
    user = User(id=str(uuid7()), email="testuser@example.com", username="testuser1234", password="password")
    org = Organization(id=str(uuid.uuid4()), name="Test Organization")
    test_db.add(user)
    test_db.add(org)
    test_db.commit()  # Commit user and organization before adding invitation

    invitation = Invitation(
        id=user.id,
        user_id=user.id,
        organization_id=org.id,
        expires_at=datetime.utcnow() + timedelta(days=1),
        is_valid=True
    )
    test_db.add(invitation)
    test_db.commit()  # Commit invitation

    invite_link = f"http://127.0.0.1:8000/api/v1/invite/accept?invitation_id={invitation.id}"
    response = client.post(
        "/api/v1/invite/accept",
        json={"invitation_link": invite_link}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "User added to organization successfully"

def test_accept_invite_expired_link(test_db):
    # Create test data
    user = User(id=str(uuid7()), email="testuser@example.com", username="testuser", password="password")
    org = Organization(id=str(uuid7()), name="Test Organization")
    test_db.add(user)
    test_db.add(org)
    test_db.commit()  # Commit user and organization before adding invitation

    invitation = Invitation(
        id=str(uuid7()),
        user_id=user.id,
        organization_id=org.id,
        expires_at=datetime.utcnow() - timedelta(days=1),
        is_valid=True
    )
    test_db.add(invitation)
    test_db.commit()  # Commit invitation

    invite_link = f"http://127.0.0.1:8000/api/v1/invite/accept?invitation_id={invitation.id}"
    response = client.post(
        "/api/v1/invite/accept",
        json={"invitation_link": invite_link}
    )
    print("JSON Response ", response.json())
    assert response.status_code == 400
    data = response.json()
    assert data["message"] == "Expired invitation link"

def test_accept_invite_malformed_link(test_db):
    invite_link = f"http://127.0.0.1:8000/api/v1/invite/accept?invitation_id=invalid-uuid"
    response = client.post(
        "/api/v1/invite/accept",
        json={"invitation_link": invite_link}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["message"] == "Invalid invitation link"

def test_load_testing_accept_invite(test_db):
    # Create test data
    user = User(id=str(uuid7()), email="testuser@example.com", username="testuser", password="password")
    org = Organization(id=str(uuid7()), name="Test Organization")
    test_db.add(user)
    test_db.add(org)
    test_db.commit()  # Commit user and organization before adding invitation

    invitation = Invitation(
        id=str(uuid7()),
        user_id=user.id,
        organization_id=org.id,
        expires_at=datetime.utcnow() + timedelta(days=1),
        is_valid=True
    )
    test_db.add(invitation)
    test_db.commit()  # Commit invitation

    invite_link = f"http://127.0.0.1:8000/api/v1/invite/accept?invitation_id={invitation.id}"

    # Perform load testing
    num_requests = 10
    responses = [
        client.post(
            "/api/v1/invite/accept",
            json={"invitation_link": invite_link}
        )
        for _ in range(num_requests)
    ]

    successful_responses = [r for r in responses if r.status_code == 200]
    assert len(successful_responses) == 1  # Only one should succeed
    for r in responses:
        if r.status_code == 200:
            data = r.json()
            assert data["status"] == "success"
            assert data["message"] == "User added to organization successfully"
        else:
            data = r.json()
            assert data["message"] in ["Invitation not found or already used", "User already in organization"]
