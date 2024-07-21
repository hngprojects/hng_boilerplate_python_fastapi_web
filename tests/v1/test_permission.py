import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import timedelta

# Add the parent directory of the project to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from main import app
from api.db.database import get_db
from api.v1.models.permission import Permission
from api.v1.models.user import User
from api.utils.auth import create_access_token, hash_password

client = TestClient(app)

# Mock the database dependency
@pytest.fixture
def db_session_mock(mocker):
    db_session = mocker.MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(mocker, db_session_mock):
    mocker.patch("api.v1.routes.permission_router.get_db", return_value=db_session_mock)

@pytest.fixture
def auth_headers(db_session_mock):
    # Create a test admin user
    test_admin = User(
        username="admin",
        email="admin@example.com",
        password=hash_password("adminpassword"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_admin=True
    )
    db_session_mock.query(User).filter(User.username == "admin").first.return_value = test_admin

    # Generate token
    token = create_access_token({"sub": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to API",
        "URL": "",
    }

@pytest.mark.permission
def test_create_permission(db_session_mock, auth_headers):
    # Arrange
    db_session_mock.query(Permission).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    permission_data = {"name": "test_permission", "description": "Test Permission"}

    # Act
    response = client.post("/api/v1/permissions", json=permission_data, headers=auth_headers)

    # Assert
    assert response.status_code == 201
    assert "id" in response.json()["data"]

@pytest.mark.permission
def test_get_permissions(db_session_mock, auth_headers):
    # Arrange
    db_session_mock.query(Permission).all.return_value = []

    # Act
    response = client.get("/api/v1/permissions", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

@pytest.mark.permission
def test_get_permission(db_session_mock, auth_headers):
    # Arrange
    permission = Permission(name="test_permission_to_get", description="Test Permission to Get")
    db_session_mock.query(Permission).filter_by(id=1).first.return_value = permission

    # Act
    response = client.get(f"/api/v1/permissions/1", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "test_permission_to_get"

@pytest.mark.permission
def test_update_permission(db_session_mock, auth_headers):
    # Arrange
    permission = Permission(name="test_permission_to_update", description="Test Permission to Update")
    db_session_mock.query(Permission).filter_by(id=1).first.return_value = permission

    update_data = {"name": "updated_test_permission", "description": "Updated Test Permission"}

    # Act
    response = client.put(f"/api/v1/permissions/1", json=update_data, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "updated_test_permission"

@pytest.mark.permission
def test_delete_permission(db_session_mock, auth_headers):
    # Arrange
    permission = Permission(name="test_permission_to_delete", description="Test Permission to Delete")
    db_session_mock.query(Permission).filter_by(id=1).first.return_value = permission

    # Act
    response = client.delete(f"/api/v1/permissions/1", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Permission deleted successfully."

if __name__ == "__main__":
    pytest.main()
