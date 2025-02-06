import pytest
from fastapi.testclient import TestClient
from api.db.database import SessionLocal
from main import app
from api.db.database import get_db
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from api.v1.models.user import User

client = TestClient(app)
data1 = {
    "first_name": "Marvelous",
    "last_name": "Uboh",
    "password": "Doyinsola174@$",
    "email": "utibesolomon12@gmail.com"
}
data2 = {

    "first_name": "Marvelou",
    "last_name": "Ubh",
    "password": "Doyinsola177@$",
    "email": "utibesolomon15@gmail.com"

}
data3 = {

    "first_name": "Marvelu",
    "last_name": "Ubah",
    "password": "Doyinsola179@$",
    "email": "utibesolomon17@gmail.com"
    
}
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield
    # Clean up after the test by removing the override
    app.dependency_overrides = {}

@pytest.mark.parametrize('data', [data1, data2, data3])
def test_super_user_creation(data, db_session_mock):


    db_session_mock.query().filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    # Mock the user creation function

    url = '/api/v1/auth/register-super-admin'
   
  
    response = client.post(url, json=data)

    
    assert response.json()['message'] == 'User created successfully'
    assert response.status_code == 201
    # Assert that create_user was called with the correct data
   
    db_session_mock.query().filter().first.return_value = data

    data.pop('email')
    invalid_data_response = client.post(url, json=data)
    assert invalid_data_response.status_code == 422