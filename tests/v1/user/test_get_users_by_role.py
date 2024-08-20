import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from api.v1.models.user import User
from api.v1.models.organisation import Organisation
from api.v1.models.user import user_organisation_association
from api.v1.services.user import user_service, UserService
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone
from sqlalchemy.orm import Session


client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."

    Yields:
        MagicMock: mock database
    """

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


mock_id = str(uuid7())



def test_get_user_by_role(mock_db_session):
    # Create a mock user

    mock_id = "mock_user_id"
    dummy_mock_user = User(
        id=mock_id,
        email="dummyuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Mr",
        last_name="Dummy",
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db_session.query().filter().first.return_value = dummy_mock_user 


    '''First Login'''
    url = 'api/v1/auth/login'
    login_response = client.post(url,json={'email':'dummyuser1@gmail.com', 'password': 'Testpassword@123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']
    user_id = login_response.json()['data']['user']['id']

    role_id = "owner"    

    # Test endpoint without organisation

    get_user_response = client.get(f'api/v1/users/{role_id}/roles', headers={
        'Authorization': f'Bearer {access_token}'
    })
    assert get_user_response.status_code == 403
    assert get_user_response.json()['message'] == 'Permission denied. Admin access required.'
