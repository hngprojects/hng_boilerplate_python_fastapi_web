import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from unittest.mock import Mock
from sqlalchemy.orm import Session

from main import app
from api.db.database import get_db
from api.v1.models.terms import TermsAndConditions
from api.v1.schemas.terms_and_conditions import UpdateTermsAndConditions
from api.v1.services.user import user_service

@pytest.fixture
def mock_db():
    return Mock(spec=Session)


@pytest.fixture
def mock_current_user():
    user = Mock()
    user.is_superadmin = True
    user.id = 1
    return user

@pytest.fixture
def client(mock_db, mock_current_user):
    def override_get_db():
        return mock_db

    def override_get_current_super_admin():
        return mock_current_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[user_service.get_current_super_admin] = override_get_current_super_admin
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


def test_create_terms_and_conditions_success(client, mock_db, mock_current_user):
    # Prepare test data
    test_data = {
        "title": "Test Terms and Conditions",
        "content": "This is a test content for terms and conditions."
    }

    # Mock database query
    mock_db.query.return_value.first.return_value = None

    # Send POST request
    response = client.post("/api/v1/terms-and-conditions", json=test_data)

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Successfully created terms and conditions"
    assert "data" in response.json()
    assert response.json()["data"]["title"] == test_data["title"]
    assert response.json()["data"]["content"] == test_data["content"]

    # Verify mock calls
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_terms_and_conditions_already_exists(client, mock_db, mock_current_user):
    # Prepare test data
    test_data = {
        "title": "New Terms and Conditions",
        "content": "This should not be created."
    }

    # Mock existing terms and conditions
    mock_existing_tc = Mock(spec=TermsAndConditions)
    mock_db.query.return_value.first.return_value = mock_existing_tc

    # Send POST request
    response = client.post("/api/v1/terms-and-conditions", json=test_data)

    # Assert response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["message"] == "Terms and conditions already exist. Use PATCH to update."

    # Verify mock calls
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()

def test_create_terms_and_conditions_unauthorized(client, mock_db,):
    # mock get_current_super_admin function
    def mock_get_current_super_admin():
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource",
        )

    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_super_admin

    test_data = {
        "title": "Test Terms and Conditions",
        "content": "This should not be created due to lack of authorization."
    }

    response = client.post("/api/v1/terms-and-conditions/", json=test_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides.clear()