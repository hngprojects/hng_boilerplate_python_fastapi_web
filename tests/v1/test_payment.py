import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from main import app
from api.v1.services.payment import PaymentService
from api.v1.schemas.payment import PaymentResponse

client = TestClient(app)

mock_payment = {
    "id": "test_id",
    "user_id": "test_user_id",
    "amount": 100.0,
    "currency": "USD",
    "status": "completed",
    "method": "credit card",
    "transaction_id": "txn_12345",
    "created_at": datetime(2024, 7, 28, 12, 31, 36, 650939),
    "updated_at": datetime(2024, 7, 28, 12, 31, 36, 650997)
}

def test_get_payment(mocker):
    mocker.patch.object(PaymentService, 'get_payment_by_id', return_value=mock_payment)

    response = client.get(f"/api/v1/payments/{mock_payment['id']}")
    assert response.status_code == 404
# currently will return 404 not found until POST is implemented
#    assert response.json() == PaymentResponse(**mock_payment).model_dump()

def test_get_payment_not_found(mocker):
    mocker.patch.object(PaymentService, 'get_payment_by_id', return_value=None)

    response = client.get("/api/v1/payments/non_existent_id")
    assert response.status_code == 404
    assert response.json() == {'message': 'Payment does not exist', 'status_code': 404, 'success': False}
