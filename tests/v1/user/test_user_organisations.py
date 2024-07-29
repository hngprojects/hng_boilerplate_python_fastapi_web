import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest import mock
from api.db.database import Base, get_db
from main import app
from api.v1.models.user import User
from api.v1.models.organization import Organization
from api.v1.services.user import user_service

DATABASE_URL = "postgresql://freeman:2234@localhost:5432/hng_fast_api"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def test_user(test_db):
    user = User(email="test@example.com", password="testpassword", is_super_admin=False)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture(scope="module")
def test_super_user(test_db):
    super_user = User(email="superuser@example.com", password="superpassword", is_super_admin=True)
    test_db.add(super_user)
    test_db.commit()
    test_db.refresh(super_user)
    return super_user

@pytest.fixture(scope="module")
def test_organization(test_db, test_user):
    organization = Organization(company_name="Test Organization")
    organization.users.append(test_user)
    test_db.add(organization)
    test_db.commit()
    test_db.refresh(organization)
    return organization

@pytest.fixture(scope="module")
def access_token(test_user):
    return user_service.create_access_token(user_id=test_user.id)

@pytest.fixture(scope="module")
def super_access_token(test_super_user):
    return user_service.create_access_token(user_id=test_super_user.id)

def test_get_user_organizations(client, access_token, test_organization):
    response = client.get(
        "/api/v1/organizations/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status_code"] == 200
    assert response.json()["message"] == "Organizations retrieved successfully"
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["company_name"] == test_organization.company_name

def test_get_all_organizations_super_user(client, super_access_token, test_organization):
    response = client.get(
        "/api/v1/organizations/",
        headers={"Authorization": f"Bearer {super_access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status_code"] == 200
    assert response.json()["message"] == "Organizations retrieved successfully"
    assert len(response.json()["data"]) > 0  # Superuser should see all organizations
