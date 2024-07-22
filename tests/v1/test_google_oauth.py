#!/usr/bin/env python3
"""
Unittests to mock google oauth2
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from httpx import AsyncClient
from main import app
from api.utils.config import oauth


return_value = {
    'access_token': 'ya29.a0AXooCgsyqTjEeoFljLum4zscdvf0Bv4Xrh5Kdnm_2wefaiDSEVey7-4DYZRDXTg493-PTDY4frVQreJGY-F5ZZoFZgne-TI7waYlFHZamn_NmOWjuQcBf_RHqXdZ_-F2mG79p16aYnV7ct_YNwW5HdXTHUbcigTxMvIsaCgYKAZsSARMSFQHGX2Mixa3CyZRXHTeluL75KEbYrw0171',
    'expires_in': 3599,
    'scope': 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid',
    'token_type': 'Bearer',
    'id_token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6aevbgsd1ZmQ3ZTRhOTcyNzFkZmZhOTkxZjVhODkzY2QxNmI4ZTA4MjciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIyMDk2Nzg2NzcxNTktc3JvNzF0bjcycHVvdG5wcGFzMHMwdDUyajgyOWNxOGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIyMDk2Nzg2NzcxNTktc3JvNzF0bjcycHVvdG5wcGFzMHMwdDUyajgyOWNxOGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTQxMzI5ODk5NzMxNDQ1MzI2MzciLCJlbWFpbCI6IjN4c2FpbnRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJoRF9VdWY5aWJUY0dYc0RQMV9lUGd3Iiwibm9uY2UiOiJhRWJrNHlBN3dadFhKQ3ZCcm15TCIsIm5hbWUiOiJKb2huc29uIE9yYWd1aSIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NMWkRQSjBjSy1kd0VfZmNqVjl5ajczVGlEVFdDRGwxUG5YYld3NTZkcS1xWktONTJRPXM5Ni1jIiwiZ2l2ZW5fbmFtZSI6IkpvaG5zb24iLCJmYW1pbHlfbmFtZSI6Ik9yYWd1aSIsImlhdCI6MTcyMTQ4OTMxMSwiZXhwIjoxNzIxNDkyOTExfQ.Pc1LfLtJo_OGY8vBR9eL2smLUaQPM3SgmL9Fq0IXYSYDN2pVJYsB33Ku6r7KGGFOxRDnPM3Jm8b8cuC93yaiY61LySMMlXPQk_Lm0jNNrFQefifmRUf54AZXLsg8CnIovrD46A7b0WhJxEfbF0Ni4bxRIzb2EghUr42FdN3i0PIwd_9dSFyRaywt_S2sLBqr6wU7VbGQ5ZlRBLfkuJP7FT-GHuyee65hY9hiKGgQhBrDuZOeJjQfgLnwyv3n5tKyomtqjSe9BTnseRET5NzFLf_55zlz_OvI2Bn7gk1sqZ1ek4QLyOLsKdaaM8xWusgcMe84PCuC3xy7coL9_mGQBw',
    'expires_at': 1721492909,
    'userinfo': {
        'iss': 'https://accounts.google.com',
        'azp': '209678677159-sro71tn72puotnppasrtgv52j829cq8g.apps.googleusercontent.com',
        'aud': '209678677159-sro71tn72puotnppas0jnmj52j829cq8g.apps.googleusercontent.com',
        'sub': '114132989973144532376',
        'email': 'johnson.oragui@gmail.com',
        'email_verified': True,
        'at_hash': 'hD_Uuf9ibTsxXsDP1_ePgw',
        'nonce': 'aEbk4yA7wZtXazvBrmyL',
        'name': 'Johnson Oragui',
        'picture': 'https://lh3.googleusercontent.com/a/ACg8rdfcvg0cK-dwE_fcjV9yj7yhnjiWCDl1PnXbWw56dq-qZKN52Q=s96-c',
        'given_name': 'Johnson',
        'family_name': 'Oragui',
        'iat': 1721489311,
        'exp': 1721492911
        }
}

@pytest.fixture
def client():
    client = TestClient(app)
    return client

@pytest.fixture
def mock_google_oauth2():
    with patch.object(oauth.google, 'authorize_redirect') as mock_authorize_redirect:
        with patch.object(oauth.google, 'authorize_access_token') as mock_authorize_token_userinfo:
            with patch.object(oauth.google, 'parse_id_token') as _:
                mock_authorize_redirect.return_value = "http://testserver/api/v1/auth/login/google"
                mock_authorize_token_userinfo.return_value = return_value

                yield mock_authorize_redirect, mock_authorize_token_userinfo

def test_login(client, mock_google_oauth2):
    response = client.get("/auth/login/google")
    print("response: ", response)
    assert response.status_code == 200
    assert response.url == "http://testserver/api/v1/auth/login/google"

def test_auth(client, mock_google_oauth2):
    response = client.get("/auth/callback/google?code=fake-code")
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data["data"]
    assert 'refresh_token' in data["data"]
