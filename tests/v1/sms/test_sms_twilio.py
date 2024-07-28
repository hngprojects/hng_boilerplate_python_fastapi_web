import pytest
from unittest.mock import Mock
from api.v1.routes.sms_twilio import send_sms
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock

user_id = str(uuid7())
client = TestClient(app)

@pytest.fixture
def mock_twilio_client(mocker):
    # Mock the Twilio client
    mock = mocker.patch('twilio.rest.Client')
    mock_instance = mock.return_value
    mock_instance.messages.create.return_value = MagicMock(status="sent")
    return mock_instance

def send_sms(client, to, body):
    return client.messages.create(to=to, body=body)

def TwilioTestClient():
    class TestClient:
        messages = Mock()
    
        def __init__(self, *args, **kwargs):
            pass

    return TestClient

def test_twilio_client(mocker):
    mock_twilio_client = mocker.patch("api.v1.services.sms_twilio.client", TwilioTestClient())
    send_sms(mock_twilio_client, "+1234567890", "Hello, World!")
    mock_twilio_client.messages.create.assert_called_once_with(to="+1234567890", body="Hello, World!")
    

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