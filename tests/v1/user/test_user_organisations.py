import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from api.db.database import get_db, create_database
from api.v1.models.organization import Organization
from api.v1.models.user import User
from api.v1.services.user import UserService

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    """Create a new database for testing"""
    create_database()
    db = next(get_db())
    yield db
    db.close()

@pytest.fixture(scope="module")
def test_user(test_db: Session):
    """Create a test user"""
    user_service = UserService()
    user_schema = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password",
    }
    user = user_service.create(test_db, user_schema)
    yield user

@pytest.fixture(scope="module")
def auth_token(test_user: User, test_db: Session):
    """Create a valid token for the test user"""
    user_service = UserService()
    token = user_service.create_access_token(user_id=test_user.id)
    return token

def test_get_user_organizations(test_db: Session, auth_token: str):
    """Test retrieving organizations for the current user"""
    # Create organizations for the user
    organization_data = [
        {"name": "Org1", "description": "Test Organization 1", "user_id": "test_user.id"},
        {"name": "Org2", "description": "Test Organization 2", "user_id": "test_user.id"},
    ]
    for data in organization_data:
        org = Organization(**data)
        test_db.add(org)
    test_db.commit()

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/v1/organizations/current-user", headers=headers)

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["data"][0]["name"] == "Org1"
    assert response.json()["data"][1]["name"] == "Org2"

