import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

url = "/api/v1"


def create_permission(client, name: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name
    }
    response = client.post(f"{url}/permissions", headers=headers, json=data)
    print("permission: ", response.json())
    assert response.status_code == 201

def create_organization(client, name: str, desc: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    org_data = {
        "name": name,
        "description": desc
    }
    response = client.post(f"{url}/organizations", json=org_data, headers=headers)
    print("organization: ", response.json())
    assert response.status_code == 201  # Assuming 201 is the status code for successful creation
    return response.json()["id"]

def create_user(client, username: str, password: str):
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

def get_auth_token(client, username: str, password: str):
    login_data = {
        "username": username,
        "password": password
    }
    response = client.post(f"{url}/auth/login", data=login_data)
    print("token: ", response.json()) 
    assert response.status_code == 200
    return response.json()["access_token"]

def create_role(client, token: str, role_name: str, organization_id: str, permission_ids: list = None):
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

def test_create_role(client):
    
    # Create a user
    username = "admin"
    password = "admin12345"
    create_user(client, username=username, password=password)
    
    # # Get authentication token
    token = get_auth_token(client, username=username, password=password)
    # print(token)

    # # Create an organization
    organization_id = create_organization(client, desc="Test Organization", name="Mba", token=token)
    permission = create_permission(client, name="Read", token=token)
    
    # # Create a role
    role_name = "Manager1"
    permission = ["Read"]
    create_role(client, token=token, role_name=role_name, organization_id=organization_id, permission_ids=permission)

