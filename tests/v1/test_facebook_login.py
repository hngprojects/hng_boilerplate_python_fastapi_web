import pytest
import requests
from fastapi import status

# Assuming there's a running instance of the application
BASE_URL = "http://localhost:7001"
VALID_TOKEN = "XXXXXXXX" # This token needs to be a valid token for the test to pass

def test_facebook_login_success():
    # This token needs to be a valid token for the test to pass
    valid_token = VALID_TOKEN
    response = requests.post(f"{BASE_URL}/api/v1/auth/facebook-login", json={"access_token": valid_token})
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    assert "data" in response.json()
    assert "access_token" in response.json().get("data")

def test_facebook_login_invalid_token():
    invalid_token = "XXXXXXX"
    response = requests.post(f"{BASE_URL}/api/v1/auth/facebook-login", json={"access_token": invalid_token})
    print(response.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "error" in response.json()

def test_facebook_api_failure():
    response = requests.post(f"{BASE_URL}/api/v1/auth/facebook-login", json={"access_token": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "error" in response.json()

def test_facebook_api_invalid_request():
    response = requests.post(f"{BASE_URL}/api/v1/auth/facebook-login", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
