import pytest
from fastapi.testclient import TestClient
from main import app  # Update this import based on your actual app module
from unittest.mock import MagicMock
import jwt
from pydantic import ValidationError
from api.v1.services.user import user_service
from uuid_extensions import uuid7

client = TestClient(app)

user_id = str(uuid7())

@pytest.fixture
def mock_twilio_client(mocker):
    # Mock the Twilio client
    mock = mocker.patch('twilio.rest.Client')
    mock_instance = mock.return_value
    mock_instance.messages.create.return_value = MagicMock(status="sent")
    return mock_instance

@pytest.fixture
def set_env_vars(monkeypatch):
    # Set environment variables for Twilio
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "fake_sid")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "fake_token")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+1234567890")

def test_send_sms_success(mock_twilio_client):
    phone_number = "+254796200725"
    message = "Hello from HNG"
    access_token = user_service.create_access_token(str(user_id))
    response = client.post(
        "/api/v1/sms/send",
        json={"phone_number": phone_number, "message": message},
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    print("Send SMS response:", response.json())  # Debugging output
    
    assert response.status_code == 200

def test_send_sms_error_invalid_phone_number(mock_twilio_client):
    phone_number = "+25467uf445"
    message = "Hello from HNG"
    access_token = user_service.create_access_token(str(user_id))
    response = client.post(
        "/api/v1/sms/send",
        json={"phone_number": phone_number, "message": message},
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    print("Invalid phone number response:", response.json())  # Debugging output
    
    assert response.status_code == 422

def test_send_sms_error_empty_message(mock_twilio_client):
    phone_number = "+254796200725"
    message = ""
    access_token = user_service.create_access_token(str(user_id))
    response = client.post(
        "/api/v1/sms/send",
        json={"phone_number": phone_number, "message": message},
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    print("Empty message response:", response.json())  # Debugging output
    
    assert response.status_code == 422
