import pytest
from jose import jwt
from decouple import config
from api.v1.models.user import User
from api.v1.models.user import ShowUser
from api.utils.oauth2 import Token, TokenData

import json


SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config("ALGORITHM")


payload = {
    "first_name": "test",
    "last_name": "user",
    "email": "test@gmail.com",
    "password": "password123",
    "unique_id": "1005"
}

def test_create_user(client):
    
    res = client.post(
        "/signup/", data=(json.dumps(payload)))

    new_user = ShowUser(**res.json()['data'])
    assert new_user.email==payload['email']
    assert res.status_code == 201


def test_login_user(test_user, client):
    res = client.post(
        "/login", data=json.dumps({"email": test_user['email'], "password": "password123"}))

    logged_in_user = ShowUser(**res.json()['data'])
    payload = jwt.decode(res.json()['access_token'],
                         SECRET_KEY, algorithms=[ALGORITHM])
    id = payload.get("id")
    token_type= res.json()['token_type']
    assert id == test_user['id']
    assert logged_in_user.email == test_user['email']
    assert token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 401),
    ('dean@gmail.com', 'wrongpassword', 401),
    ('wrongemail@gmail.com', 'wrongpassword', 401),
    (None, 'password123', 422),
    ('test@gmail.com', None, 422)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post(
        "/login", data=json.dumps({"email": email, "password": password}))

    assert res.status_code == status_code