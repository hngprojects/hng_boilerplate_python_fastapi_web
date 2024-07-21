import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from main import app
from api.db.database import Base, get_db
from api.utils.auth import hash_password
from api.v1.models.user import User
from api.v1.models.permission import Permission

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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


@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()

def create_user(test_db):
    # Add user to database
    user = User(
        username="testuser",
        email="testuser@gmail.com",
        password=hash_password('Testpassword@123'),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_admin=True  # Ensure user is admin to create permissions
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

def test_create_permission(test_db):
    create_user(test_db)
    
    login = client.post('/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']

    response = client.post(
        "/api/v1/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "test_permission", "description": "Test Permission"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_permission"
    assert data["description"] == "Test Permission"

def test_create_permission_duplicate_name(test_db):
    login = client.post('/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']

    # Create the first permission
    response = client.post(
        "/api/v1/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "duplicate_permission", "description": "Test Permission"}
    )
    assert response.status_code == 201

    # Attempt to create a permission with an existing name
    response = client.post(
        "/api/v1/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "duplicate_permission", "description": "Test Permission Duplicate"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Permission already exists."}

def test_create_permission_unauthorized(test_db):
    response = client.post(
        "/api/v1/permissions",
        headers={"Authorization": "Bearer invalid-token"},
        json={"name": "unauthorized_permission", "description": "This should not be created."}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

def test_get_permissions(test_db):
    login = client.post('/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']

    response = client.get("/api/v1/permissions", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_permission(test_db):
    login = client.post('/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']

    permission = Permission(name="test_permission_to_get", description="Test Permission to Get")
    test_db.add(permission)
    test_db.commit()
    test_db.refresh(permission)

    response = client.get(f"/api/v1/permissions/{permission.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_permission_to_get"

def test_update_permission(test_db):
    login = client.post('/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']

    permission = Permission(name="test_permission_to_update", description="Test Permission to Update")
    test_db.add(permission)
    test_db.commit()
    test_db.refresh(permission)

    update_data = {"name": "updated_test_permission", "description": "Updated Test Permission"}
    response = client.put(f"/api/v1/permissions/{permission.id}", json=update_data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_test_permission"

def test_delete_permission(test_db):
    login = client.post('/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']

    permission = Permission(name="test_permission_to_delete", description="Test Permission to Delete")
    test_db.add(permission)
    test_db.commit()
    test_db.refresh(permission)

    response = client.delete(f"/api/v1/permissions/{permission.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Permission deleted successfully."}
