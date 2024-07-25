import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.v1.models.profile import Profile  # Import the Profile model
from sqlalchemy.orm import Session
from api.db.database import get_db

client = TestClient(app)


# Mock the database session dependency
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock


# Test fixtures for users and access tokens
@pytest.fixture
def test_admin():
    return User(
        id="admin_id",  # Ensure the admin has an ID
        username="admin",
        email="admin@example.com",
        is_super_admin=True,
    )


@pytest.fixture
def test_customer():
    user = User(
        id="customer_id",  # Ensure the customer has an ID
        username="customer",
        email="customer@example.com",
        first_name="John",
        last_name="Doe",
    )
    profile = Profile(
        user_id=user.id,  # Link profile to the user
        phone_number="1234567890",
        bio="Customer biography",
        avatar_url="http://example.com/avatar.jpg"
    )
    user.profile = profile
    return user


@pytest.fixture
def access_token_admin(test_admin):
    return user_service.create_access_token({"sub": test_admin.username})


# Test successful customer update
def test_update_customer_success(mock_db_session, test_customer, access_token_admin):
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_customer
    headers = {'Authorization': f'Bearer {access_token_admin}'}
    update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "phone_number": "0987654321",  # Updated to match the `Profile` schema
    }
    response = client.put(f"/api/v1/customers/{test_customer.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()['data']['first_name'] == "Jane"
    assert response.json()['data']['last_name'] == "Smith"
    assert response.json()['data']['phone_number'] == "0987654321"


# Test missing fields in update
def test_update_customer_partial_success(mock_db_session, test_customer, access_token_admin):
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_customer
    headers = {'Authorization': f'Bearer {access_token_admin}'}
    update_data = {
        "phone_number": "0987654321",
    }
    response = client.put(f"/api/v1/customers/{test_customer.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()['data']['phone_number'] == "0987654321"
    assert response.json()['data']['first_name'] == test_customer.first_name  # Check that other fields remain unchanged


# Test unauthorized access
def test_update_customer_unauthorized(mock_db_session, test_customer):
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_customer
    update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
    }
    response = client.put(f"/api/v1/customers/{test_customer.id}", json=update_data)
    assert response.status_code == 401  # Expecting 401 Unauthorized
