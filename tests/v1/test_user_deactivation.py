import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.utils.password_auth import hash_password
from api.db.database import Base, get_db
from api.v1.models.user import User
from api.v1.models.base import Base


test_db_name = 'test_fastapi_db'
test_db_pw = 'postgres' 
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:{test_db_pw}@localhost:5432/{test_db_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables in the test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
	db = TestingSessionLocal()
	yield db
	db.close()


def test_user_deactivation(db):
    '''Test for user deactivation'''

    # Add user to database
    user = User(
        username="testuser",
        email="testuser@gmail.com",
        password=hash_password("testpassword"),
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)


    login =  client.post('/api/v1/auth/login', json={
        "username": "testuser",
        "password": "testpassword"
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
    assert user_already_deactivated.json()['detail'] == 'Confirmation required to deactivate account'


    unauthorized = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": True
    })
    assert unauthorized.status_code == 401


    success_deactivation = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": True
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert success_deactivation.status_code == 200
	

    user_already_deactivated = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": False
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert user_already_deactivated.status_code == 400
    assert user_already_deactivated.json()['detail'] == 'User is inactive'
