# import pytest
# from fastapi.testclient import TestClient
# from main import app
# from unittest.mock import MagicMock
# # from api.utils.auth import hash_password
# from api.v1.models.user import User
# from api.db.database import get_db

# client = TestClient(app)

# # Mock the database dependency
# @pytest.fixture
# def db_session_mock():
#     db_session = MagicMock()
#     yield db_session


# @pytest.fixture(autouse=True)
# def override_get_db(db_session_mock):
#     def get_db_override():
#         yield db_session_mock
#     app.dependency_overrides[get_db] = get_db_override


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from main import app
from api.db.database import Base, get_db
from api.utils.auth import hash_password
from api.v1.models.user import User
from api.v1.models.base import Base

SQLALCHEMY_DATABASE_URL = config('DB_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
	db = TestingSessionLocal()
	yield db
	db.close()
	

def create_user(test_db):
	
    # Add user to database
    user = User(
        username="testuser",
        email="testuser@gmail.com",
        password=hash_password('Testpassword@123'),
		first_name='Test',
		last_name='User',
        is_active=True,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)


def error_user_deactivation(test_db):
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
	

def success_deactivation_test(test_db):
	
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
	

def test_iser_inactive(test_db):
	
    user = User(
        username="testuser1",
        email="testuser1@gmail.com",
        password=hash_password('Testpassword@123'),
		first_name='Test',
		last_name='User',
        is_active=False,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
	
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
	