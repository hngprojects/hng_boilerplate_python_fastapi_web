from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
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


def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="test@gmail.com",
        password=user_service.hash_password("Testuser@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

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
        title="Inquiry about services",
        message="Hello, I would like more information about your services and pricing.",
        org_id=mock_org().id
    )


def test_post_contact_us(client, db_session_mock):
    '''Test to successfully create a new product category'''

    from api.v1.services.contact_us import contact_us_service

    app.dependency_overrides[contact_us_service.create] = lambda: mock_contact_us

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_contact_instance = mock_contact_us()


    with patch("api.v1.services.contact_us.contact_us_service.create", return_value=mock_contact_instance) as mock_create:

        response = client.post('/api/v1/contact', json={
            "full_name": "Josh Oloton",
            "email": "josh@example.com",
            "phone_number": "07017796046",
            "message": "I can't log in to my account",
            "org_id": mock_org().id
        })

        print(response.json())
        assert response.status_code == 201


def test_post_contact_us_missing_fields(client, db_session_mock):
    '''Test to unsuccessfully create a new product category with missing fields'''

    from api.v1.services.contact_us import contact_us_service

    app.dependency_overrides[contact_us_service.create] = lambda: mock_contact_us

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_contact_instance = mock_contact_us()


    with patch("api.v1.services.contact_us.contact_us_service.create", return_value=mock_contact_instance) as mock_create:

        response = client.post('/api/v1/contact', json={
            "email": "josh@example.com",
            "message": "I can't log in to my account",
        })

        print(response.json())
        assert response.status_code == 422