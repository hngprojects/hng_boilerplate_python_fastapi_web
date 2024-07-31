import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from unittest.mock import MagicMock
from api.v1.models import Organization, User
from api.v1.models.associations import user_organization_association
from api.v1.services.user import user_service
from api.db.database import get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)

# Dependency override for database session
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Dependency override for current user
def override_get_current_user():
    return 1  # Mock current user as owner with user_id=1

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[user_service.get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    yield db
    db.close()

def test_delete_organization_owner(db, mocker):
    # Mock data setup
    user = User(
        id=1, 
        email="owner@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_super_admin=True,
        )
    organization = Organization(id=1, company_name="Test Org", company_email="test_org@gmail.com")

     # Mock db.add and db.commit
    db_mock = mocker.MagicMock()
    db_instance = db_mock.return_value
    db_instance.query.return_value.filter.return_value.one.side_effect = [organization, {'user_id': 1}]
    
    with mocker.patch('api.db.database.get_db', return_value=db_instance):
        db_instance.add.side_effect = None  # No-op
        db_instance.commit.side_effect = None  # No-op

        # Mock the connection and the insert execution
        conn_mock = mocker.patch('sqlalchemy.engine.Engine.connect')
        execute_mock = mocker.patch('sqlalchemy.engine.Connection.execute')
        conn_mock.return_value.__enter__.return_value.execute = execute_mock

        response = client.delete("/organizations/1")
        assert response.status_code == 204


# def test_delete_organization_non_owner(db, mocker):
#     # Mock data setup
#     user = User(id=1, username="owner")
#     another_user = User(id=2, username="non_owner")
#     organization = Organization(id=1, name="Test Org")
#     user_organization = user_organization_association(user_id=1, organization_id=1, role="member")
    
#     db.add(user)
#     db.add(another_user)
#     db.add(organization)
#     db.add(user_organization)
#     db.commit()

#     # Override current user to be a non-owner
#     app.dependency_overrides[user_service.get_current_user] = lambda: 2

#     # Mock the query to return the organization and user_organization
#     mocker.patch('main.Session.query', side_effect=lambda model: {
#         Organization: MagicMock(return_value=MagicMock(filter=MagicMock(one=MagicMock(return_value=organization)))),
#         user_organization_association: MagicMock(return_value=MagicMock(filter=MagicMock(one=MagicMock(return_value=user_organization))))
#     }[model])

#     response = client.delete("/organizations/1")
#     assert response.status_code == 403
#     assert response.json() == {"detail": "Only the owner can delete the organization"}

#     # Reset dependency override
#     app.dependency_overrides[user_service.get_current_user] = override_get_current_user
