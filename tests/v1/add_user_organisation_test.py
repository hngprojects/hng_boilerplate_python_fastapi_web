import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.db.database import get_db
from fastapi import status

client = TestClient(app)

# Mock data
mock_user = User(id=1)
mock_org = Organization(id=1, users=[mock_user])

# Test successful user addition
@patch('api.db.database.get_db')
@patch('api.v1.routes.organization.get_current_user')
def test_add_user_to_organization_success(mock_get_current_user, mock_get_db):
    # Mock the current user and database session
    mock_get_current_user.return_value = mock_user
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # Set up mock database methods
    mock_db.query.return_value.filter.return_value.first.return_value = mock_org

    # Send a POST request to the endpoint
    response = client.post('/api/v1/organization/1/add-user', json={})

    # Assert the response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "success",
        "message": "User added to organisation successfully",
    }

# Test organization not found
@patch('api.db.database.get_db')
@patch('api.v1.routes.organization.get_current_user')
def test_add_user_to_organization_org_not_found(mock_get_current_user, mock_get_db):
    # Mock the current user and database session
    mock_get_current_user.return_value = mock_user
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # Set up mock database methods to return None for organization
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Send a POST request to the endpoint
    response = client.post('/api/v1/organization/1/add-user', json={})

    # Assert the response
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Organization not found"}

# Test user not found
@patch('api.db.database.get_db')
@patch('api.v1.routes.organization.get_current_user')
def test_add_user_to_organization_user_not_found(mock_get_current_user, mock_get_db):
    # Mock the current user and database session
    mock_get_current_user.return_value = mock_user
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # Set up mock database methods for organization
    mock_db.query.return_value.filter.return_value.first.return_value = mock_org

    # Set up mock database methods for user to return None
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Send a POST request to the endpoint
    response = client.post('/api/v1/organization/1/add-user', json={})

    # Assert the response
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}

# Test user already a member
@patch('api.db.database.get_db')
@patch('api.v1.routes.organization.get_current_user')
def test_add_user_to_organization_user_already_member(mock_get_current_user, mock_get_db):
    # Mock the current user and database session
    mock_get_current_user.return_value = mock_user
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # Set up mock database methods for organization with user already a member
    mock_org.users.append(mock_user)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_org

    # Send a POST request to the endpoint
    response = client.post('/api/v1/organization/1/add-user', json={})

    # Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "User is already a member of the organization"}
