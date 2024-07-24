import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


data1 = {
    "first_name": "Marvelous",
    "last_name": "Uboh",
    "username": "marveld0",
    "password": "Doyinsola174@$",
    "email": "utibesolomon12@gmail.com"
}
data2 = {

    "first_name": "Marvelou",
    "last_name": "Ubh",
    "username": "marveldoes",
    "password": "Doyinsola177@$",
    "email": "utibesolomon15@gmail.com"

}
data3 = {

    "first_name": "Marvelu",
    "last_name": "Ub",
    "username": "marveldid",
    "password": "Doyinsola179@$",
    "email": "utibesolomon17@gmail.com"

}

@pytest.mark.parametrize('data', [data1, data2, data3])
def test_super_user_creation(data):
    url = '/api/v1/superadmin/register'
    response = client.post(url, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == 'User Created Successfully'
   ## REPEATING THE QUERY TO ASSERT BAD REQUEST FOR ALREADY EXISITNG ACCOUNT
    
    repeat_query = client.post(url, json = data)
    assert repeat_query.status_code == 400
    

 ##Removing One field from the data to assert 422 Error
    data.pop('email')
    Another_query = client.post(url , json= data)
    assert Another_query.status_code == 422









