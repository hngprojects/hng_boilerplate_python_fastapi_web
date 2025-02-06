import pytest
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from main import app
from api.db.database import get_db
from api.v1.models import User, Payment
from api.v1.services.user import user_service

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

# Test User
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )

@pytest.fixture()
def test_payment(test_user):
    payment = Payment(
        id=str(uuid7()),
        amount=5000.00,
        currency="Naira",
        status="completed",
        method="debit card",
        user_id=test_user.id,
        transaction_id=str(uuid7()),
        created_at=datetime.now(tz=timezone.utc)
    )

    return payment

@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)

@pytest.fixture
def random_access_token():
    return user_service.create_access_token(user_id=str(uuid7()))


# Test for successful retrieve of payments
def test_get_payments_successfully(
    mock_db_session,
    test_user,
    test_payment,
    access_token_user
):
    # Mock the query for getting user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    # TEST A SINGLE PAYMENT FOR 1-PAGE RESULT #

    # Mock the query for payments
    mock_db_session.query.return_value.filter.return_value\
        .offset.return_value.limit.return_value.all.return_value = [test_payment]

    # Make request
    params = {'page': 1, 'limit': 10}
    headers = {'Authorization': f'Bearer {access_token_user}'}
    response = client.get("/api/v1/transactions/current-user", params=params, headers=headers)

    resp_d = response.json()

    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "Payments fetched successfully"

    pagination = resp_d['data']['pagination']
    assert pagination['limit'] == 10
    assert pagination['total_items'] == 1
    assert pagination['total_pages'] == 1

    payments = resp_d['data']['payments']
    assert len(payments) == 1

    pay = payments[0]
    assert float(pay['amount']) == test_payment.amount
    assert pay['currency'] == test_payment.currency
    assert pay['status'] == test_payment.status
    assert pay['method'] == test_payment.method
    assert datetime.fromisoformat(pay['created_at']) == test_payment.created_at

    # RESET MOCK PAYMENTS TO SIMULATE MULTI-PAGE RESULT #

    # Mock the query for payments, this time for 5 payments
    five_payments = [test_payment, test_payment, test_payment, test_payment, test_payment]
    mock_db_session.query.return_value.filter.return_value\
        .offset.return_value.limit.return_value.all.return_value = five_payments

    # Make request, with limit set to 2, to get 3 pages
    params = {'page': 1, 'limit': 2}
    headers = {'Authorization': f'Bearer {access_token_user}'}
    response = client.get("/api/v1/transactions/current-user", params=params, headers=headers)

    resp_d = response.json()

    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "Payments fetched successfully"
    assert resp_d['data']['user_id'] == test_user.id

    pagination = resp_d['data']['pagination']
    assert pagination['limit'] == 2
    assert pagination['total_items'] == 5
    assert pagination['total_pages'] == 3

    payments = resp_d['data']['payments']
    assert len(payments) == 5


# Test for un-authenticated request
def test_for_unauthenticated_get_payments(
    mock_db_session,
    test_user,
    test_payment,
    access_token_user
):
    params = {'page': 1, 'limit': 10}

    # Mock the query for getting user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    # Make request || WRONG Authorization
    headers = {'Authorization': f'Bearer {random_access_token}'}
    response = client.get("/api/v1/transactions/current-user", params=params, headers=headers)

    assert response.status_code == 401
    assert response.json()['message'] == "Could not validate credentials"
    assert not response.json().get('data')

    # Make request || NO Authorization
    response = client.get("/api/v1/transactions/current-user", params=params)

    assert response.status_code == 401
    assert response.json()['message'] == "Not authenticated"
    assert not response.json().get('data')


# Test for no payment for user
def test_for_no_payments_for_user(
    mock_db_session,
    test_user,
    test_payment,
    access_token_user
):
    # Mock the query for getting user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    # Mock the query for payments
    mock_db_session.query.return_value.filter.return_value\
        .offset.return_value.limit.return_value.all.return_value = []

    # Make request
    params = {'page': 1, 'limit': 10}
    headers = {'Authorization': f'Bearer {access_token_user}'}
    response = client.get("/api/v1/transactions/current-user", params=params, headers=headers)

    assert response.status_code == 404
    assert response.json()['message'] == "Payments not found for user"
    assert not response.json().get('data')
