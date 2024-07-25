import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from main import app
from api.v1.models.payment import Payment
from api.v1.models.user import User
from api.v1.routes.get_payments import get_db
from api.v1.services.user import user_service


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
    
    db_session_mock.query().all.return_value = []

    
    with patch.object(user_service, 'get_current_user', return_value=current_user_mock):
    
        response = client.get("/api/v1/payments")

    
    assert response.status_code == 200
    assert response.json()["data"] == []

def test_get_all_payments_with_data(client, db_session_mock, current_user_mock):
    
    payments = [
        Payment(
            id=1,
            user_id="testuser_id",
            amount=100.0,
            currency="USD",
            status="completed",
            method="credit card",
            transaction_id="trans_001"
        ),
        Payment(
            id=2,
            user_id="testuser_id",
            amount=200.0,
            currency="USD",
            status="pending",
            method="PayPal",
            transaction_id="trans_002"
        )
    ]

    
    db_session_mock.query().all.return_value = payments

    
    with patch.object(user_service, 'get_current_user', return_value=current_user_mock):
    
        response = client.get("/api/v1/payments")

    
    assert response.status_code == 200
    assert response.json()["data"] == [
        {
            "id": 1,
            "user_id": "testuser_id",
            "amount": 100.0,
            "currency": "USD",
            "status": "completed",
            "method": "credit card",
            "transaction_id": "trans_001"
        },
        {
            "id": 2,
            "user_id": "testuser_id",
            "amount": 200.0,
            "currency": "USD",
            "status": "pending",
            "method": "PayPal",
            "transaction_id": "trans_002"
        }
    ]
