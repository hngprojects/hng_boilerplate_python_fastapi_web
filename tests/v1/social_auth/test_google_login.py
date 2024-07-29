import pytest
from fastapi import status, HTTPException
from unittest.mock import patch, MagicMock
from google.auth.exceptions import GoogleAuthError
from api.v1.services.google_oauth import GoogleOauthServices


@pytest.fixture
def mock_db_session():
    db_session = MagicMock()
    return db_session

@pytest.fixture
def google_oauth_service():
    return GoogleOauthServices()

@pytest.fixture
def mock_id_info():
    return {
        'email': 'johnson@example.com',
        'sub': '1234567890',
        'given_name': 'johnson',
        'family_name': 'Oragui',
        'picture': 'http://example.com/avatar.jpg'
    }

@patch('google.oauth2.id_token.verify_oauth2_token')
@patch('api.v1.services.google_oauth.user_service.create_access_token')
def test_verify_google_token_success(mock_create_access_token, mock_verify_oauth2_token, mock_id_info, google_oauth_service, mock_db_session):
    mock_verify_oauth2_token.return_value = mock_id_info
    mock_create_access_token.return_value = 'mock_access_token'

    access, refresh = google_oauth_service.verify_google_token('mock_token', mock_db_session)
    
    assert access == 'mock_access_token'
    assert refresh == 'mock_access_token'
    mock_verify_oauth2_token.assert_called_once()
    mock_create_access_token.assert_called()

@patch('google.oauth2.id_token.verify_oauth2_token', side_effect=GoogleAuthError)
def test_verify_google_token_invalid_token(mock_verify_oauth2_token, google_oauth_service, mock_db_session):
    with pytest.raises(HTTPException) as exc_info:
        google_oauth_service.verify_google_token('mock_token', mock_db_session)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"
    mock_verify_oauth2_token.assert_called_once()

@patch('google.oauth2.id_token.verify_oauth2_token', side_effect=ValueError)
def test_verify_google_token_value_error(mock_verify_oauth2_token, google_oauth_service, mock_db_session):
    with pytest.raises(HTTPException) as exc_info:
        google_oauth_service.verify_google_token('mock_token', mock_db_session)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"
    mock_verify_oauth2_token.assert_called_once()

@patch('google.oauth2.id_token.verify_oauth2_token')
@patch('api.v1.services.google_oauth.user_service.create_access_token', side_effect=Exception("Token creation failed"))
def test_generate_tokens_failure(mock_create_access_token, mock_verify_oauth2_token, mock_id_info, google_oauth_service, mock_db_session):
    mock_verify_oauth2_token.return_value = mock_id_info

    access, refresh = google_oauth_service.verify_google_token('mock_token', mock_db_session)
    
    assert access == False
    assert refresh == False
    mock_verify_oauth2_token.assert_called_once()
    mock_create_access_token.assert_called()
