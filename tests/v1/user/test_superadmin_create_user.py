import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from main import app
from api.db.database import get_db

from api.v1.schemas.user import  AdminCreateUserResponse, UserData
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

def test_superadmin_create_user(mock_superadmin, mock_token_verification,
                                user_service_mock, mock_db_session):
    """
    Test for super admin to create a new user
    """
    created_at = datetime.now()
    updated_at = datetime.now()
    user = User(
                id="user_id_1",
                email="new_user1@email.com",
                first_name="new_user",
                last_name="new_user",
                is_active=True,
                is_deleted=False,
                is_verified=True,
                is_superadmin=False,
                created_at=created_at.isoformat(),
                updated_at=updated_at.isoformat()
            )

    headers = {
        'Authorization': f'Bearer fake_token'
    }
    user_request = {'email': 'new_user1@email.com', 'first_name': 'new_user',
             'last_name': 'new_user', 'password': 'new_user_password',
              'is_active': True, 'is_deleted': False,
             'is_verified': True, 'is_superadmin': False, 'created_at': created_at.isoformat(),
             'updated_at': updated_at.isoformat()
    }
    (mock_db_session.query.return_value
                 .filter_by.return_value
                 .one_or_none.return_value) = None

    user_response = AdminCreateUserResponse(
        message='User created successfully',
        status_code=201,
        status='success',
        data= UserData.model_validate(user, from_attributes=True)

    )
    user_service_mock.super_admin_create_user.return_value = user_response
    
    mock_user = MagicMock()
    mock_user.id = "user_id_1"
    
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda x: (
        setattr(x, 'id', mock_user.id),
        setattr(x, 'created_at', created_at),
        setattr(x, 'updated_at', updated_at)
    )
    
    response = client.post(f"/api/v1/users", json=user_request, headers=headers)

    print(response.json())
    
    assert response.status_code == 201
    
    assert response.json() == {
        'message': 'User created successfully',
        'status': 'success',
        'status_code': 201,
        'data': {
                'id': 'user_id_1',
                'email': user_request['email'],
                'first_name': user_request['first_name'],
                'last_name': user_request['last_name'],
                'is_active': True,
                'is_deleted': False,
                'is_verified': True,
                'is_superadmin': False,
                'created_at': created_at.isoformat(),
                'updated_at': updated_at.isoformat()
        }
    }
