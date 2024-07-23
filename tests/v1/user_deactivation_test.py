import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app
from api.db.database import Base, get_db
from api.v1.services.user import user_service
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
        password=user_service.hash_password('Testpassword@123'),
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
	

def success_deactivation_test(test_db):
	
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
	

def test_user_inactive(test_db):
	
    user = User(
        username="testuser1",
        email="testuser1@gmail.com",
        password=user_service.hash_password('Testpassword@123'),
		first_name='Test',
		last_name='User',
        is_active=False,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
	
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
	

# import pytest
# from fastapi.testclient import TestClient
# from unittest.mock import patch, MagicMock
# import sys, os
# import warnings

# warnings.filterwarnings("ignore", category=DeprecationWarning)
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# from main import app
# from api.v1.models.user import User

# client = TestClient(app)

# @pytest.fixture
# def mock_db_session():
#     """Fixture to create a mock database session."""
#     with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
#         mock_db = MagicMock()
#         mock_get_db.return_value.__enter__.return_value = mock_db
#         yield mock_db

# @pytest.fixture
# def mock_user_service():
#     """Fixture to create a mock user service."""
#     with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
#         yield mock_service

# def create_mock_user(mock_user_service, mock_db_session):
#     """Create a mock user in the mock database session."""
#     mock_user = User(
#         username="testuser",
#         email="testuser@gmail.com",
#         password="hashed_password",
#         first_name='Test',
#         last_name='User',
#         is_active=True,
#         is_admin=False
#     )
#     mock_db_session.query.return_value.filter.return_value.first.return_value = None
#     mock_user_service.hash_password.return_value = "hashed_password"
#     mock_db_session.add.return_value = None
#     mock_db_session.commit.return_value = None
#     mock_db_session.refresh.return_value = None

#     return mock_user

# @pytest.mark.usefixtures("mock_db_session", "mock_user_service")
# def test_error_user_deactivation(mock_user_service, mock_db_session):
#     """Test for user deactivation errors."""
#     create_mock_user(mock_user_service, mock_db_session)

#     login = client.post('/api/v1/auth/login', data={
#         "username": "testuser",
#         "password": "Testpassword@123"
#     })
#     mock_user_service.authenticate_user.return_value = create_mock_user(mock_user_service, mock_db_session)
#     access_token = login.json()['data']['access_token']

#     # Missing field test
#     missing_field = client.post('/api/v1/users/deactivation', json={
#         "reason": "No longer need the account"
#     }, headers={'Authorization': f'Bearer {access_token}'})
#     assert missing_field.status_code == 422

#     # Confirmation false test
#     confirmation_false = client.post('/api/v1/users/deactivation', json={
#         "reason": "No longer need the account",
#         "confirmation": False
#     }, headers={'Authorization': f'Bearer {access_token}'})
#     assert confirmation_false.status_code == 400
#     assert confirmation_false.json()['message'] == 'Confirmation required to deactivate account'

#     # Unauthorized test
#     unauthorized = client.post('/api/v1/users/deactivation', json={
#         "reason": "No longer need the account",
#         "confirmation": True
#     })
#     assert unauthorized.status_code == 401

# @pytest.mark.usefixtures("mock_db_session", "mock_user_service")
# def test_success_deactivation(mock_user_service, mock_db_session):
#     """Test for successful user deactivation."""
#     create_mock_user(mock_user_service, mock_db_session)

#     login = client.post('api/v1/auth/login', data={
#         "username": "testuser",
#         "password": "Testpassword@123"
#     })
#     mock_user_service.authenticate_user.return_value = create_mock_user(mock_user_service, mock_db_session)
#     access_token = login.json()['data']['access_token']

#     success_deactivation = client.post('/api/v1/users/deactivation', json={
#         "reason": "No longer need the account",
#         "confirmation": True
#     }, headers={'Authorization': f'Bearer {access_token}'})
#     assert success_deactivation.status_code == 200

# @pytest.mark.usefixtures("mock_db_session", "mock_user_service")
# def test_user_inactive(mock_user_service, mock_db_session):
#     """Test for inactive user deactivation."""
#     mock_user = User(
#         username="testuser1",
#         email="testuser1@gmail.com",
#         password="hashed_password",
#         first_name='Test',
#         last_name='User',
#         is_active=False,
#         is_admin=False
#     )
#     mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
#     mock_user_service.hash_password.return_value = "hashed_password"
#     mock_db_session.add.return_value = None
#     mock_db_session.commit.return_value = None
#     mock_db_session.refresh.return_value = None

#     login = client.post('/api/v1/auth/login', data={
#         "username": "testuser1",
#         "password": "Testpassword@123"
#     })
#     mock_user_service.authenticate_user.return_value = mock_user
#     access_token = login.json()['data']['access_token']

#     user_already_deactivated = client.post('/api/v1/users/deactivation', json={
#         "reason": "No longer need the account",
#         "confirmation": True
#     }, headers={'Authorization': f'Bearer {access_token}'})

#     assert user_already_deactivated.status_code == 400
#     assert user_already_deactivated.json()['message'] == 'User is inactive'
