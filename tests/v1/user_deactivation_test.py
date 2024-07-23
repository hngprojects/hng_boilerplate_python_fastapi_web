import pytest
from tests.database import client, session
import sys, os
import warnings
from api.v1.models import *
from api.v1.services.user import user_service

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def create_user(client, session):
	
    # Add user to database
    user = User(
        username="testuser",
        email="testuser@gmail.com",
        password=user_service.hash_password('Testpassword@123'),
		first_name='Test',
		last_name='User',
        is_active=True,
        is_admin=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)


def error_user_deactivation(client, session):
    '''Test for user deactivation'''

    login =  client.post('/api/v1/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['data']['access_token']


    missing_field = client.post('/api/v1/users/deactivation', json={
        "reason": "No longer need the account"
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert missing_field.status_code == 422


    confirmation_false = client.post('/api/v1/users/deactivation', json={
        "reason": "No longer need the account",
        "confirmation": False
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert confirmation_false.status_code == 400
    assert confirmation_false.json()['message'] == 'Confirmation required to deactivate account'


    unauthorized = client.post('/api/v1/users/deactivation', json={
        "reason": "No longer need the account",
        "confirmation": True
    })
    assert unauthorized.status_code == 401
	

def success_deactivation_test(client, session):
	
    login =  client.post('/api/v1/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']
	
    success_deactivation = client.post('/api/v1/users/deactivation', json={
        "reason": "No longer need the account",
        "confirmation": True
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert success_deactivation.status_code == 200
	

def test_user_inactive(client, session):
	
    user = User(
        username="testuser1",
        email="testuser1@gmail.com",
        password=user_service.hash_password('Testpassword@123'),
		first_name='Test',
		last_name='User',
        is_active=False,
        is_admin=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
	
    login =  client.post('/api/v1/auth/login', data={
        "username": "testuser1",
        "password": "Testpassword@123"
    })
    access_token = login.json()['data']['access_token']

	
    user_already_deactivated = client.post('/api/v1/users/deactivation', json={
        "reason": "No longer need the account",
        "confirmation": True
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert user_already_deactivated.status_code == 403
    assert user_already_deactivated.json()['message'] == 'User is not active'
