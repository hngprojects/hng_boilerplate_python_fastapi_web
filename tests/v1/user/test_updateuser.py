import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service, UserService
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone
from sqlalchemy.orm import Session


client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."

    Yields:
        MagicMock: mock database
    """

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


mock_id = str(uuid7())

@pytest.fixture
def mock_get_current_user():
    """Fixture to create a mock current user"""
    with patch(
        "api.v1.services.user.UserService.get_current_user", autospec=True
    ) as mock_get_current_user:
        yield mock_get_current_user




   



def test_update_user(mock_db_session):
    dummy_mock_user =  User(
        id=mock_id,
        email= "Testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Mr",
        last_name="Dummy",
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    app.dependency_overrides[user_service.get_current_super_admin] = lambda: User(
        id=str(uuid7()),
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="AdminTest",
        last_name="User",
        is_active=False,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
  

    """Testing the endpoint with an authorized user"""
    data = {
        "first_name": "AdminTest"
    }
    
    mock_db_session.query().filter().first.return_value = False
    mock_db_session.get.return_value = dummy_mock_user
    
    get_user_url = f'api/v1/users/{dummy_mock_user.id}'
    
    get_user_response = client.patch(get_user_url,json=data)
    assert get_user_response.status_code == 200
    assert get_user_response.json()['message'] == 'User Updated Successfully'
    assert get_user_response.json()['data']['first_name'] == data['first_name']

    """Testing endpoint with an unauthorized user"""

    app.dependency_overrides[user_service.get_current_super_admin] = user_service.get_current_super_admin

    """Login"""
    
    get_bad_response = client.patch(get_user_url,json=data)

    assert get_bad_response.status_code == 401


def test_current_user_update(mock_db_session):
    dummy_mock_user =  User(
        id=mock_id,
        password=user_service.hash_password("Testpassword@123"),
        first_name="Mr",
        last_name="Dummy",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    data = {
        "first_name": "Mr"
    }
    app.dependency_overrides[user_service.get_current_user] = lambda : dummy_mock_user

    mock_db_session.query().filter().first.return_value = False
    mock_db_session.get.return_value = dummy_mock_user
    get_user_url = 'api/v1/users'
    get_response = client.patch(get_user_url,json=data)
    assert get_response.status_code == 200
    assert get_response.json()['message'] == 'User Updated Successfully'
    assert get_response.json()['data']['first_name'] == data['first_name']

