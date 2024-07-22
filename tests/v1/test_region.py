import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust the Python path to include the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from main import app
from api.v1.models.base import Base
from api.utils.auth import hash_password
from api.v1.models.user import User
from api.v1.models.region import Region
from api.db.database import get_db

# SQLite test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create engine and session
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)


# Override dependency to use test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# Fixture for setting up and tearing down the test database
@pytest.fixture(scope="module")
def test_db():
    # Create tables before tests
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)
    db.close()


# Helper function to create a test user
def create_user(test_db):
    user = User(
        username="testuser",
        email="testuser@example.com",
        password=hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_admin=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


# Test cases
def test_create_region(test_db):
    create_user(test_db)  # Ensure a user is created
    response = client.post(
        "/api/v1/regions/",
        json={
            "region_code": "002",
            "region_name": "New Test Region",
            "status": "active",
            "created_by": 1,  # Make sure this matches the user ID
            "modified_by": 1,  # Make sure this matches the user ID
        },
    )
    assert response.status_code == 201


def test_get_regions(test_db):
    create_user(test_db)  # Ensure a user is created
    test_region = Region(
        region_code="001",
        region_name="Test Region",
        status="active",
        created_by=1,  # Make sure this matches the user ID
        modified_by=1,  # Make sure this matches the user ID
    )
    test_db.add(test_region)
    test_db.commit()

    response = client.get("/api/v1/regions/")
    assert response.status_code == 200
    regions = response.json()
    assert len(regions) > 0  # Change this if you expect no regions
