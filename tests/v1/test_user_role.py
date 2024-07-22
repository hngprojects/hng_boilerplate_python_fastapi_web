
import sys
import os
import warnings

# DB_URL = os.getenv("DB_URL")

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Append the project root directory to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from main import app
from api.db.database import Base, get_db
from api.utils.auth import hash_password
from api.v1.models.user import User
from api.v1.models.base import Base

# SQLALCHEMY_DATABASE_URL = config('DB_URL')
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db5"
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
		last_name='User'
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)


url = "/api/v1"


def create_permission(name: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name
    }
    response = client.post(f"{url}/permissions", headers=headers, json=data)
    print("permission: ", response.json())
    assert response.status_code == 201

def create_organization(name: str, desc: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    org_data = {
        "name": name,
        "description": desc
    }
    response = client.post(f"{url}/organizations", json=org_data, headers=headers)
    print("organization: ", response.json())
    assert response.status_code == 201  # Assuming 201 is the status code for successful creation
    return response.json()["id"]

def create_user(username: str, password: str):
    user_data = {
        "username": username,
        "password": password,
        "first_name": "kama",
        "last_name": "mba",
        "email": f"{username}@example.com",
        "is_admin": True
    }
    
    response = client.post(f"{url}/auth/register", json=user_data)
    print("user: ", response.json())
    assert response.status_code == 201  # Assuming 201 is the status code for successful creation
    return response.json()

def get_auth_token(username: str, password: str):
    login_data = {
        "username": username,
        "password": password
    }
    response = client.post(f"{url}/auth/login", data=login_data)
    print("token: ", response.json()) 
    assert response.status_code == 200
    return response.json()["access_token"]

def create_role(token: str, role_name: str, organization_id: str, permission_ids: list = None):
    headers = {"Authorization": f"Bearer {token}"}
    role_data = {
        "role_name": role_name,
        "organization_id": organization_id,
        "permission_ids": permission_ids
    }
    response = client.post(f"{url}/roles", headers=headers, json=role_data)
    print("role: ", response.json())
    assert response.status_code == 201  # Assuming 200 is the status code for successful creation
    return response.json()

def test_create_role():
    
    # Create a user
    username = "admin"
    password = "admin12345"
    create_user(username=username, password=password)
    
    # # Get authentication token
    token = get_auth_token(username=username, password=password)
    # print(token)

    # # Create an organization
    organization_id = create_organization(desc="Test Organization", name="Mba", token=token)
    permission = create_permission(name="Read", token=token)
    
    # # Create a role
    role_name = "Manager1"
    permission = ["Read"]
    create_role(token=token, role_name=role_name, organization_id=organization_id, permission_ids=permission)

