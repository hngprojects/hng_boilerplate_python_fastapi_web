import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from main import app  # Adjust this import according to your project structure
from api.db.database import get_db
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
def mock_token_verification():
    with patch("api.v1.services.user.UserService.verify_access_token") as mock:
        mock.return_value = MagicMock(id="superadmin_id", is_superadmin=True)
        yield mock

@pytest.fixture
def mock_superadmin():
    with patch("api.v1.services.user.UserService.get_current_super_admin") as mock:
        mock.return_value = User(id="superadmin_id", email="superadmin@example.com", password="super_admin")
        yield mock

@pytest.fixture
def mock_own_account():
    with patch("api.v1.services.user.UserService.verify_access_token") as mock:
        mock.return_value = MagicMock(id="067c1cbe-8906-7f20-8000-36d29872a571", is_superadmin=False)
        yield mock

def test_delete_user(mock_db_session, user_service_mock, mock_token_verification):
    """
    Test for deleting a user as a superadmin
    """
    user_id = "067c1cbe-8906-7f20-8000-36d29872a571"
    mock_user = User(id=user_id, email='test@email.com', first_name='Test',
                     last_name='User', is_active=True, is_deleted=False)
    
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    user_service_mock.delete_user.return_value = {"message": "User successfully deleted","success": True, "status_code": 200}
    
    headers = {
        'Authorization': 'Bearer fake_token'
    }
    response = client.delete(f"/api/v1/users/delete?user_id={user_id}", headers=headers)
    
    assert response.status_code == 200
    assert response.json() == {
        "message": "User successfully deleted",
        "status": "success",
        "status_code": 200,
        "data": {},
    }

def test_delete_user_not_superadmin(mock_db_session, user_service_mock):
    """
    Test for attempting to delete a user as a non-superadmin
    """
    user_id = "067c1cbe-8906-7f20-8000-36d29872a571"
    mock_user = User(id=user_id, email='test@email.com', first_name='Test', last_name='User', is_active=True, is_deleted=False)
    
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    mock_current_user = MagicMock(spec=User)
    mock_current_user.is_superadmin = False 
    #user_service_mock.delete_user.side_effect = None  # Ensure it does nothing
    
    headers = {
        'Authorization': 'Bearer fake_token'
    }
    response = client.delete(f"/api/v1/users/delete?user_id={user_id}", headers=headers)
    

    print(response.status_code, response.json()) # Debugging
    assert response.status_code == 401
    assert response.json() =={
        'message': 'Could not validate credentials',
        'status': False,
        'status_code': 401
}

def test_delete_own_account(mock_db_session, user_service_mock, mock_own_account):
    """
    Test for a user deleting their own account via access token
    """
    user_id = "067c1cbe-8906-7f20-8000-36d29872a571"
    mock_user = User(id=user_id, email='test@email.com', first_name='Test', last_name='User', is_active=True, is_deleted=False)
    
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    user_service_mock.delete_user.return_value = {"message": "User successfully deleted", "status": "success", "status_code": 200}
    
    headers = {
        'Authorization': 'Bearer fake_token'
    }
    response = client.delete("/api/v1/users/delete", headers=headers)
    
    assert response.status_code == 200
    assert response.json() == {
        "message": "User successfully deleted",
        "status": "success",
        "status_code": 200,
        "data": {},
    }
