from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app
import pytest
from uuid import UUID
from api.v1.services.user import user_service

client = TestClient(app)

# Mock valid and invalid tokens
VALID_TOKEN = "valid_token"
INVALID_TOKEN = "invalid_token"

# Mock user data
MOCK_USER = {
    "id": UUID("11111111-1111-1111-1111-111111111111"),
    "email": "user@example.com",
    "name": "John Doe",
    "role": "Admin"
}

# Mock function to validate token and return user
def mock_get_current_user(token: str):
    if token == VALID_TOKEN:
        return MOCK_USER
    raise HTTPException(status_code=401, detail="Invalid token")

# Apply the mock to your dependency
app.dependency_overrides[user_service.get_current_user] = mock_get_current_user


def test_get_organization_users_success():
    org_id = "066a1121-b805-7393-8002-e20f2105f59c"
    response = client.get(f"/api/v1/organization/{org_id}/users", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 200
    data = response.json()
    assert data["org_id"] == org_id
    assert len(data["users"]) > 0
    assert all(key in data["users"][0] for key in ["id", "email", "name", "role"])

def test_get_organization_users_invalid_uuid():
    org_id = "invalid-uuid"
    response = client.get(f"/api/v1/organization/{org_id}/users", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 422

def test_get_organization_users_no_auth():
    org_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    response = client.get(f"/api/v1/organization/{org_id}/users")
    assert response.status_code == 401 

def test_get_organization_users_invalid_token():
    org_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    response = client.get(f"/api/v1/organization/{org_id}/users", headers={"Authorization": f"Bearer {INVALID_TOKEN}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
