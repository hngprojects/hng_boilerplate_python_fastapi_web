import pytest
from fastapi.testclient import TestClient
from main import app
from api.utils.auth import create_access_token
from api.v1.models.user import User
from sqlalchemy.orm import Session
from api.db.database import get_db

client = TestClient(app)

# Mock the database session dependency
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

@pytest.fixture
def test_user1():
    return User(
        username="testuser12",
        email="testuser12@example.com",
        password="hashedpassword",
        first_name="Test1",
        last_name="User1",
        is_active=True,
        is_admin=True
    )

@pytest.fixture
def test_user2():
    return User(
        username="testuser13",
        email="testuser13@example.com",
        password="hashedpassword",
        first_name="Test2",
        last_name="User2",
        is_active=True,
        is_admin=False
    )

@pytest.fixture
def test_user3():
    return User(
        username="testuser14",
        email="testuser14@example.com",
        password="hashedpassword",
        first_name="Test3",
        last_name="User3",
        is_active=False,
        is_admin=True
    )

@pytest.fixture
def access_token_user1():
    return create_access_token(data={"username": "testuser12"})

@pytest.fixture
def access_token_user2():
    return create_access_token(data={"username": "testuser13"})

@pytest.fixture
def access_token_user3():
    return create_access_token(data={"username": "testuser14"})

# Testing with authenticated, active admin user
def test_fetch_customers_user1(mock_db_session, test_user1, access_token_user1):
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user1
    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.get("/api/v1/customers", headers=headers)
    assert response.status_code == 200

# Testing with authenticated, active non-admin user
def test_fetch_customers_user2(mock_db_session, test_user2, access_token_user2):
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user2
    headers = {'Authorization': f'Bearer {access_token_user2}'}
    response = client.get("/api/v1/customers", headers=headers)
    assert response.status_code == 403

# Testing with authenticated, non-active admin user
def test_fetch_customers_user3(mock_db_session, test_user3, access_token_user3):
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user3
    headers = {'Authorization': f'Bearer {access_token_user3}'}
    response = client.get("/api/v1/customers", headers=headers)
    assert response.status_code == 401

# Testing with unauthenticated
def test_fetch_customers_user4(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    response = client.get("/api/v1/customers")
    assert response.status_code == 401
