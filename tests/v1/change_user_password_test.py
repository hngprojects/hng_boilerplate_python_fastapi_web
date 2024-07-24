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
        username="randomuser1",
        email="randomuser@gmail.com",
        password=user_service.hash_password('randomPwd@123'),
		first_name='Test',
		last_name='User',
        is_active=True,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)



def test_user_password(test_db):
	
    create_user(test_db)
	
    login =  client.post('/api/v1/auth/login', data={
        "username": "randomuser1",
        "password": "randomPwd@123"
    })
    print(login)
    access_token = login.json()['data']['access_token']

	
    user_pwd_change = client.patch('/api/v1/users/current-user/change-password', json={
        "old_password": "randomPwd@123",
        "new_password": 'Ojobonandom@123'
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert user_pwd_change.status_code == 200
    assert user_pwd_change.json()['message'] == 'Password Changed successfully'
	
