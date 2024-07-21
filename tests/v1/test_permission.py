import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.db.database import Base, get_db
from api.v1.models.user import User
from api.utils.auth import hash_password

# Define your test database name and password
test_db_name = 'your_test_db_name'  # put your test db name
test_db_pw = 'your_test_db_password'  # put your test db pw

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:{test_db_pw}@localhost:5432/{test_db_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables in the test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # Set up the test database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    test_user = User(
        username="admin",
        email="admin@example.com",
        password=hash_password("adminpassword"),
        first_name="Admin",
        last_name="User",
        is_active=True
    )
    db.add(test_user)
    db.commit()
    yield
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_create_permission(setup_database):
    response = client.post(
        "/api/v1/permissions",
        json={"name": "test_permission", "description": "Test Permission"}
    )
    assert response.status_code == 201
    assert "id" in response.json()["data"]

def test_get_permissions(setup_database):
    response = client.get("/api/v1/permissions")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

def test_get_permission(setup_database):
    # First, create a permission to get
    create_response = client.post(
        "/api/v1/permissions",
        json={"name": "test_permission_to_get", "description": "Test Permission to Get"}
    )
    assert create_response.status_code == 201
    permission_id = create_response.json()["data"]["id"]
    
    # Then, get the created permission
    get_response = client.get(f"/api/v1/permissions/{permission_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["name"] == "test_permission_to_get"

def test_update_permission(setup_database):
    # First, create a permission to update
    create_response = client.post(
        "/api/v1/permissions",
        json={"name": "test_permission_to_update", "description": "Test Permission to Update"}
    )
    assert create_response.status_code == 201
    permission_id = create_response.json()["data"]["id"]
    
    # Then, update the created permission
    update_response = client.put(
        f"/api/v1/permissions/{permission_id}",
        json={"name": "updated_test_permission", "description": "Updated Test Permission"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == "updated_test_permission"

def test_delete_permission(setup_database):
    # First, create a permission to delete
    create_response = client.post(
        "/api/v1/permissions",
        json={"name": "test_permission_to_delete", "description": "Test Permission to Delete"}
    )
    assert create_response.status_code == 201
    permission_id = create_response.json()["data"]["id"]
    
    # Then, delete the
