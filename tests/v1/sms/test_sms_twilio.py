import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app  

client = TestClient(app)

@pytest.fixture
def mock_twilio_client(mocker):
    mock_client = mocker.patch("api.v1.services.sms_twilio.Client")
    instance = mock_client.return_value
    mock_message = MagicMock()
    mock_message.sid = "mocked_sid"
    instance.messages.create = MagicMock(return_value=mock_message)
    return instance

@pytest.fixture
def set_env_vars(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "fake_sid")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "fake_token")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+1234567890")

def test_send_sms_success(mock_twilio_client, set_env_vars):
    phone_number = "+254796200725"
    message = "Hello from HNG"
    
    response = client.post("/api/v1/sms/send", json={"phone_number": phone_number, "message": message})
    
    assert response.status_code == 200
    response_json = response.json()
    expected_message = response_json['message']
    assert expected_message ==  "SMS sent successfully."
   

def test_send_sms_error_invalid_phone_number(mock_twilio_client, set_env_vars):
    phone_number = "+25467uf445"
    message = "Hello from HNG"
    
    response = client.post("/api/v1/sms/send", json={"phone_number": phone_number, "message": message})
    assert response.status_code == 422  
    response_json = response.json()
    error_message = response_json['errors'][0]['msg']
    expected_error_message = "Value error, Invalid phone number format"
    assert error_message == expected_error_message
 


def test_send_sms_error_empty_message(mock_twilio_client, set_env_vars):
    phone_number = "+254796200725"
    message = ""
    
    response = client.post("/api/v1/sms/send", json={"phone_number": phone_number, "message": message})
    assert response.status_code == 422  
    response_json = response.json()
    error_message = response_json['errors'][0]['msg']
    expected_error_message = "Value error, Message cannot be empty"
    assert error_message == expected_error_message


