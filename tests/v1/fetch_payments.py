import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from datetime import datetime

from main import app
from api.v1.models.payment import Payment
from api.v1.models.user import User
from api.v1.routes.get_payments import get_db
from api.v1.services.user import user_service

# Mock database dependency
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

@pytest.fixture
def current_user_mock():
    user = User(id="testuser_id", username="testuser", email="testuser@example.com")
    return user

def test_get_all_payments_empty(client, db_session_mock, current_user_mock):
    # Mock the return value for the query
    db_session_mock.query().all.return_value = []

    # Patch the get_current_user method
    with patch.object(user_service, 'get_current_user', return_value=current_user_mock):
        # Call the endpoint
        response = client.get("/api/v1/payments")

    # Assert the response
    assert response.status_code == 200
    assert response.json() == []

def test_get_all_payments_with_data(client, db_session_mock, current_user_mock):
    # Create mock payments
    payments = [
        Payment(
            id=1,
            user_id="testuser_id",
            amount=100.0,
            currency="USD",
            status="completed",
            method="credit card",
            transaction_id="trans_001",
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Payment(
            id=2,
            user_id="testuser_id",
            amount=200.0,
            currency="USD",
            status="pending",
            method="PayPal",
            transaction_id="trans_002",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]

    # Mock the return value for the query
    db_session_mock.query().all.return_value = payments

    # Patch the get_current_user method
    with patch.object(user_service, 'get_current_user', return_value=current_user_mock):
        # Call the endpoint
        response = client.get("/api/v1/payments")

    # Assert the response
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "user_id": "testuser_id",
            "amount": 100.0,
            "currency": "USD",
            "status": "completed",
            "method": "credit card",
            "transaction_id": "trans_001",
            "created_at": payments[0].created_at.isoformat(),
            "updated_at": payments[0].updated_at.isoformat()
        },
        {
            "id": 2,
            "user_id": "testuser_id",
            "amount": 200.0,
            "currency": "USD",
            "status": "pending",
            "method": "PayPal",
            "transaction_id": "trans_002",
            "created_at": payments[1].created_at.isoformat(),
            "updated_at": payments[1].updated_at.isoformat()
        }
    ]
