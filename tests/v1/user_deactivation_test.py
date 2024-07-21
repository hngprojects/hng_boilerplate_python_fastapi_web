import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
# from api.utils.auth import hash_password
from api.v1.models.user import User
from api.db.database import get_db

client = TestClient(app)

# Mock the database dependency
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session


@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    app.dependency_overrides[get_db] = get_db_override
	

def create_user(db_session_mock):
	
    # Add user to database
    user = User(
        username="testuser",
        email="testuser@gmail.com",
        password="Testpassword@123",
		first_name='Test',
		last_name='User',
        is_active=True,
        is_admin=False
    )
    db_session_mock.add(user)
    db_session_mock.commit()
    db_session_mock.refresh(user)


def error_user_deactivation(db_session_mock):
    '''Test for user deactivation'''

    login =  client.post('/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']


    missing_field = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account"
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert missing_field.status_code == 422


    confirmation_false = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": False
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert confirmation_false.status_code == 400
    assert confirmation_false.json()['detail'] == 'Confirmation required to deactivate account'


    unauthorized = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": True
    })
    assert unauthorized.status_code == 401
	

def success_deactivation_test(db_session_mock):
	
    login =  client.post('/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']
	
    success_deactivation = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": True
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert success_deactivation.status_code == 200
	

def test_iser_inactive(db_session_mock):
	
    user = User(
        username="testuser1",
        email="testuser1@gmail.com",
        password="Testpassword@123",
		first_name='Test',
		last_name='User',
        is_active=False,
        is_admin=False
    )
    db_session_mock.add(user)
    db_session_mock.commit()
    db_session_mock.refresh(user)
	
    login =  client.post('/auth/login', data={
        "username": "testuser1",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']

	
    user_already_deactivated = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": True
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert user_already_deactivated.status_code == 400
    assert user_already_deactivated.json()['detail'] == 'User is inactive'
	