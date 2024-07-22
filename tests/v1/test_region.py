import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust the Python path to include the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from main import app
from api.db.database import Base, get_db
from api.utils.auth import hash_password
from api.v1.models.user import User
from api.v1.models.region import Region

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Using SQLite for testing
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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


@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def create_test_user(test_db):
    user = User(
        username="testuser",
        email="testuser@example.com",
        password=hash_password("testpassword"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_admin=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="module")
def create_region(test_db, create_test_user):
    region = Region(
        region_code="001",
        region_name="Test Region",
        status="active",
        created_by=create_test_user.id,
        modified_by=create_test_user.id,
    )
    test_db.add(region)
    test_db.commit()
    test_db.refresh(region)
    return region


def test_create_region(create_test_user):
    response = client.post(
        "/api/v1/regions/",
        json={
            "region_code": "002",
            "region_name": "New Test Region",
            "status": "active",
            "created_by": create_test_user.id,
            "modified_by": create_test_user.id,
        },
    )
    assert response.status_code == 201
    assert response.json()["region_code"] == "002"
    assert response.json()["region_name"] == "New Test Region"


def test_get_regions(create_region):
    response = client.get("/api/v1/regions/")
    assert response.status_code == 200
    regions = response.json()
    assert len(regions) > 0
    assert regions[0]["region_code"] == "001"
    assert regions[0]["region_name"] == "Test Region"


def test_create_region_missing_fields(create_test_user):
    response = client.post(
        "/api/v1/regions/",
        json={
            "region_code": "003",
            "region_name": "Incomplete Region",
            "created_by": create_test_user.id,
        },
    )
    assert response.status_code == 422  # Unprocessable Entity, missing required fields


def test_get_regions_empty(test_db):
    # Clear existing regions
    test_db.query(Region).delete()
    test_db.commit()

    response = client.get("/api/v1/regions/")
    assert response.status_code == 200
    regions = response.json()
    assert len(regions) == 0
