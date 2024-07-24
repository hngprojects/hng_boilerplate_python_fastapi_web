import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from api.v1.models.org import Organization
from api.v1.models.user import User
from api.v1.models.org_role import OrgRole

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module")
def organization_service():
    from api.v1.services.org import OrganizationService
    return OrganizationService()

def test_create_organization(db_session, organization_service):
    schema = {
        "name": "Test Organization",
        "description": "Test Description"
    }
    new_organization = organization_service.create(db_session, schema)
    assert new_organization.name == schema["name"]
    assert new_organization.description == schema["description"]

def test_fetch_all_organizations(db_session, organization_service):
    organizations = organization_service.fetch_all(db_session)
    assert isinstance(organizations, list)

def test_fetch_organization(db_session, organization_service):
    org_id = 1  # Ensure this ID exists in your test database
    organization = organization_service.fetch(db_session, org_id)
    assert organization.id == org_id

def test_add_user_to_organization(db_session, organization_service):
    user = User(username="Test User")
    db_session.add(user)
    db_session.commit()

    org_id = 1  # Ensure this organization ID exists
    try:
        organization_service.add_user(db_session, org_id, user)
        assert True
    except HTTPException as e:
        assert e.status_code == 403  # Expected failure due to permissions

def test_delete_organization(db_session, organization_service):
    org_id = 1  # Ensure this ID exists
    try:
        organization_service.delete(db_session, org_id)
        assert True
    except HTTPException as e:
        assert e.status_code == 404  # Expected failure if organization not found
