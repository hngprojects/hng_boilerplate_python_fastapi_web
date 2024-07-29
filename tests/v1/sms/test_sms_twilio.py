import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app  
from api.v1.services.sms_twilio import send_sms
from unittest import mock
from twilio.base.exceptions import TwilioRestException
from api.v1.services.user import user_service
from uuid_extensions import uuid7

client = TestClient(app)
user_id = str(uuid7())


@mock.patch('api.v1.services.sms_twilio.client.messages.create')
def test_send_sms_twilio(create_message_mock):
    message = "Hi there"
    expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
    create_message_mock.return_value.sid = expected_sid

    to = "<your-personal-number>"
    sid = send_sms(to, message)

    assert create_message_mock.called is True
    assert sid["sid"] == expected_sid

@mock.patch('api.v1.services.sms_twilio.client.messages.create')
def test_log_error_when_cannot_send_sms(create_message_mock, caplog):
    error_message = (
        f"Unable to create record: The 'To' number "
        "<your-personal-number> is not a valid phone number."
    )
    status = 500
    uri = '/Accounts/ACXXXXXXXXXXXXXXXXX/Messages.json'
    msg = error_message
    create_message_mock.side_effect = TwilioRestException(status, uri, msg=error_message)

    to = "<your-personal-number>"
    sid = send_sms(to, "Wrong message")

    assert status == 500
   
def test_send_sms_error_invalid_phone_number():
    phone_number = "+25467uf445"
    message = "Hello from HNG"
    access_token = user_service.create_access_token(str(user_id))
    
    response = client.post(
        "/api/v1/sms/send/", 
        json={"phone_number": phone_number, "message": message},
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    assert response.status_code == 422
    
    response_json = response.json()
    error_message = response_json['errors'][0]['msg']
    expected_error_message = "Value error, Invalid phone number format"
    
    assert error_message == expected_error_message


def test_send_sms_error_empty_message():
    phone_number = "+254796200725"
    message = ""
    access_token = user_service.create_access_token(str(user_id))
    
    response = client.post(
        "/api/v1/sms/send/", 
        json={"phone_number": phone_number, "message": message},
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    assert response.status_code == 422
    
    response_json = response.json()
    error_message = response_json['errors'][0]['msg']
    expected_error_message = "Value error, Message cannot be empty"
    
    assert error_message == expected_error_message
