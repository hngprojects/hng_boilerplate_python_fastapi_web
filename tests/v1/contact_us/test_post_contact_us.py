from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.utils.send_mail import send_contact_mail
from api.v1.models.contact_us import ContactUs
from api.v1.models.organisation import Organisation
from api.v1.services.user import user_service
from api.v1.models.user import User
from main import app



@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def mock_org():
    return Organisation(
        id=str(uuid7()),
        name="Test Organisation",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_contact_us():
    return ContactUs(
        id=str(uuid7()), 
        full_name="Jane Doe",
        email="jane.doe@example.com",
        title="08058878456",
        message="Hello, I would like more information about your services and pricing.",
        org_id=mock_org().id
    )

@patch('fastapi.BackgroundTasks.add_task')
@patch("api.v1.services.contact_us.contact_us_service.create")
def test_post_contact_us(mock_create, mock_add_task, db_session_mock, client):
    '''Test to successfully create a new contact request'''

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_create.return_value = mock_contact_us()
    # mock_email_send.return_value = None

    response = client.post('/api/v1/contact', json={
        "full_name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone_number": "08058878456",
        "message": "Hello, I would like more information about your services and pricing.",
        "org_id": mock_org().id
    })

    print(response.json())
    assert response.status_code == 201

    # Assert that the contact_us_service.create was called with the expected arguments
    mock_create.assert_called_once()

    mock_add_task.assert_called_once()
    mock_add_task.assert_called_with(
            send_contact_mail,
            context={
                "full_name": "Jane Doe",
                "email": "jane.doe@example.com",
                "phone": "08058878456",
                "message": "Hello, I would like more information about your services and pricing.",
            }
        )


@patch('fastapi.BackgroundTasks.add_task')
@patch("api.v1.services.contact_us.contact_us_service.create")
def test_post_contact_missing_fields(mock_create, mock_add_task, db_session_mock, client):
    '''Test to unsuccessfully create a new contact request withz category'''

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_create.return_value = mock_contact_us()

    response = client.post('/api/v1/contact', json={
        "email": "jane.doe@example.com",
        "message": "Hello, I would like more information about your services and pricing.",
    })

    print(response.json())
    assert response.status_code == 422


