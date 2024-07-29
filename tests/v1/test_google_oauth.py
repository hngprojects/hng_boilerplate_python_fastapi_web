#!/usr/bin/env python3
"""
Unittests to mock google oauth2
"""
import os
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch
from main import app
from api.core.dependencies.google_oauth_config import google_oauth
from api.db.database import engine
from sqlalchemy.orm import Session, sessionmaker
from api.v1.models.user import User
from api.v1.models.oauth import OAuth
from api.v1.models.profile import Profile

SessionFactory: Session = sessionmaker(bind=engine, autoflush=False)

user_id: str = ""

return_value = {
    'access_token': 'EVey7-4DYZRDXTg493-w0171...',
    'expires_in': 3599,
    'scope': 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid',
    'token_type': 'Bearer',
    'id_token': 'eyJhbGciOiJSUcoL9_mGQBw...',
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
        'family_name': 'oragui',
        'iat': 1721489311,
        'exp': 1721492911
        }
}

@pytest.fixture(scope="session", autouse=True)
def db_teardown():
    yield
    session: Session = SessionFactory()
    try:
        session.query(Profile).delete()
        session.query(OAuth).delete()
        session.query(User).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    # finally:
    #     session.close()

@pytest.fixture
def client():
    client = TestClient(app)
    os.environ['TESTING'] = 'TEST'
    return client


@pytest.fixture
def mock_google_oauth2():
    with patch.object(google_oauth.google, 'authorize_redirect') as mock_authorize_redirect:
        with patch.object(google_oauth.google, 'authorize_access_token') as mock_authorize_token_userinfo:
            with patch.object(google_oauth.google, 'parse_id_token') as _:
                mock_authorize_redirect.return_value = "http://testserver/api/v1/auth/google"
                mock_authorize_token_userinfo.return_value = return_value


                yield mock_authorize_redirect, mock_authorize_token_userinfo


def test_google_login(client, mock_google_oauth2):
    """
    Test for google_login function redirect to google oauth
    """
    response = client.get("/api/v1/auth/google")
    assert response.status_code == 200
    assert response.url == "http://testserver/api/v1/auth/google"


def test_login_callback_oauth(client, mock_google_oauth2):
    """
    Test for google_login callback function/route
    """
    response = client.get("/api/v1/auth/callback/google?code=fake-code", follow_redirects=False)
    print(response.headers, response.has_redirect_location)
    print(response.headers['location'])
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "http://127.0.0.1:3000/dashboard/products"
    assert response.cookies


def test_database_for_user_data():
    """
    Tests if the data were stored in the users table
    """
    global user_id
    session: Session = SessionFactory()
    email = return_value['userinfo']['email']
    user: object = session.query(User).filter_by(email=email).first()
    user_id = user.id

    assert user.first_name == 'Johnson'
    assert user.last_name == 'oragui'
    assert user.email == 'johnson.oragui@gmail.com'

    session.close()

def test_database_for_oauth_data():
    """
    Tests if the data were stored in the oauth table
    """
    global user_id
    session = SessionFactory()
    oauth = session.query(OAuth).filter_by(user_id=user_id).first()

    assert oauth.access_token == return_value['access_token']
    assert oauth.refresh_token == ''
    assert oauth.sub == return_value['userinfo']['sub']

    session.close()

def test_database_for_profile_data():
    """
    Tests if the avatar_url were stored in the profile table
    """
    global user_id
    session = SessionFactory()

    user_profile = session.query(Profile).filter_by(user_id=user_id).one_or_none()

    assert user_profile.avatar_url == return_value['userinfo']['picture']

    session.close()