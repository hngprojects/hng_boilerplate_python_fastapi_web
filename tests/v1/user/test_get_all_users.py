import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from main import app  # Adjust this import according to your project structure
from api.db.database import get_db

from api.v1.schemas.user import  AllUsersResponse, UserData
from api.v1.models.user import User
from api.v1.services.user import UserService


client = TestClient(app)


@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    yield session


@pytest.fixture
def user_service_mock():
    return MagicMock()


# Overriding the dependency
@pytest.fixture(autouse=True)
def override_get_db(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session


@pytest.fixture(autouse=True)
def override_User_services(user_service_mock):
    app.dependency_overrides[UserService] = lambda: user_service_mock

@pytest.fixture
def mock_superadmin():
    with patch("api.v1.services.user.UserService.get_current_super_admin") as mock:
        mock.return_value = User(id="superadmin_id", email="superadmin@example.com", password="super_admin")
        yield mock

@pytest.fixture
def mock_token_verification():
    with patch("api.v1.services.user.UserService.verify_access_token") as mock:
        mock.return_value = MagicMock(id="superadmin_id", is_superadmin=True)
        yield mock

def test_get_all_users(mock_db_session, user_service_mock, mock_superadmin, mock_token_verification):
    """
    Test for retrieving all users
    """
    created_at = datetime.now()
    updated_at = datetime.now()
    page = 1
    per_page = 10
    mock_users = [
        User(id='admin_id', email='admin@email.com', first_name='admin',
             last_name='admin', password='super_admin', created_at=created_at,
             updated_at=updated_at, is_active=True, is_deleted=False,
             is_verified=True, is_superadmin=False),
        User(id='user_id', email='user@email.com', first_name='admin',
                          last_name='admin', password='my_password', created_at=created_at, updated_at=updated_at, is_active=True, is_deleted=False,
                          is_verified=True, is_superadmin=False)
    ]
    
    (mock_db_session
     .query.return_value
     .order_by.return_value
     .limit.return_value
     .offset.return_value.
     all.return_value) = mock_users

    mock_db_session.query.return_value.count.return_value = len(mock_users)
    
    user_service_mock.fetch_all.return_value = AllUsersResponse(
        message='Users successfully retrieved',
        status='success',
        page=page,
        per_page=per_page,
        status_code=200,
        total=len(mock_users),
        data=[UserData(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=True,
            is_deleted=False,
            is_verified=True,
            is_superadmin=False,
            created_at=user.created_at,
            updated_at=updated_at
        ) for user in mock_users]
    )
    headers = {
        'Authorization': f'Bearer fake_token'
    }
    response = client.get(f"/api/v1/users?page={page}&per_page={per_page}", headers=headers)
    print(response.json())
    
    assert response.json().get('status_code') == 200
    
    assert response.json() == {
        'message': 'Users successfully retrieved',
        'status': 'success',
        'status_code': 200,
        'page': page,
        'per_page': per_page,
        'total': len(mock_users),
        'data': [
            {
                'id': mock_users[0].id,
                'email': mock_users[0].email,
                'first_name': mock_users[0].first_name,
                'last_name': mock_users[0].last_name,
                'is_active': True,
                'is_deleted': False,
                'is_verified': True,
                'is_superadmin': False,
                'created_at': mock_users[0].created_at.isoformat(),
                'updated_at': updated_at.isoformat()
            },
            {
                'id': mock_users[1].id,
                'email': mock_users[1].email,
                'first_name': mock_users[1].first_name,
                'last_name': mock_users[1].last_name,
                'is_active': True,
                'is_deleted': False,
                'is_verified': True,
                'is_superadmin': False,
                'created_at': mock_users[1].created_at.isoformat(),
                'updated_at': updated_at.isoformat()
            }
        ]
    }
    