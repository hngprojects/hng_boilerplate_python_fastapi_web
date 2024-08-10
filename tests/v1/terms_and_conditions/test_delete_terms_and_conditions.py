from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from fastapi import HTTPException
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.v1.models.terms import TermsAndConditions
from api.v1.services.terms_and_conditions import terms_and_conditions_service
from main import app

def mock_get_current_super_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_terms_and_conditions():
    return TermsAndConditions(
        id=str(uuid7()),
        title="Test Terms and Conditions",
        content="Test Content",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

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

def test_delete_terms_and_conditions_success(client, db_session_mock):
    '''Test to successfully delete terms and conditions'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_super_admin

    mock_terms_and_conditions_instance = mock_terms_and_conditions()

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_terms_and_conditions_instance
    db_session_mock.delete.return_value = None
    db_session_mock.commit.return_value = None

    with patch("api.v1.services.terms_and_conditions.terms_and_conditions_service.delete", return_value={
        "message": "Terms and Conditions deleted successfully",
        "status_code": 200,
        "success": True,
        "data": {"terms_id": mock_terms_and_conditions_instance.id}
    }) as mock_delete:
        response = client.delete(
            f'api/v1/terms-and-conditions/{mock_terms_and_conditions_instance.id}',
            headers={'Authorization': 'Bearer token'},
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "Terms and Conditions deleted successfully",
            "status_code": 200,
            "success": True,
            "data": {"terms_id": mock_terms_and_conditions_instance.id}
        }

def test_delete_terms_and_conditions_not_found(client, db_session_mock):
    '''Test when terms and conditions are not found'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_super_admin

    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with patch("api.v1.services.terms_and_conditions.terms_and_conditions_service.delete", side_effect=HTTPException(status_code=404, detail="Terms and Conditions not found")) as mock_delete:
        response = client.delete(
            f'api/v1/terms-and-conditions/non-existing-id',
            headers={'Authorization': 'Bearer token'},
        )

        assert response.status_code == 404
        assert response.json() == {'message': 'Terms and Conditions not found', 'status': False, 'status_code': 404}

def test_delete_terms_and_conditions_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''

    mock_terms_and_conditions_instance = mock_terms_and_conditions()

    response = client.delete(
        f'api/v1/terms-and-conditions/{mock_terms_and_conditions_instance.id}',
    )

    assert response.status_code == 401
