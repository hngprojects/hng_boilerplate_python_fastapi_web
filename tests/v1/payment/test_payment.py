import pytest
from fastapi import HTTPException, status
from datetime import datetime
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
from api.v1.services.user import user_service
from api.v1.services.payment import PaymentService
from api.v1.schemas.payment import PaymentResponse
from api.utils.db_validators import check_model_existence
from api.db.database import get_db
from uuid_extensions import uuid7
from datetime import timezone
from api.v1.models.user import User
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

@pytest.fixture
def db_session_mock():
    db = MagicMock()
    yield db

@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield
    # Clean up after the test by removing the override
    app.dependency_overrides = {}


mock_user =   User(
        id=str(uuid7()),
        email="dummyuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Mr",
        last_name="Dummy",
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_get_payment(mocker):
    mocker.patch.object(PaymentService, 'get_payment_by_id', return_value=mock_payment)

    response = client.get(f"/api/v1/transactions/{mock_payment['id']}")
    assert response.status_code == 200
#    assert response.json() == PaymentResponse(**mock_payment).model_dump()

def test_get_payment_not_found(mocker):
    mocker.patch.object(PaymentService, 'get_payment_by_id', side_effect=HTTPException(status_code=404, detail='Payment does not exist'))

    response = client.get("/api/v1/transactions/non_existent_id")
    assert response.status_code == 404

def test_get_payments_by_user_id(db_session_mock):
    app.dependency_overrides[user_service.get_current_user] = lambda : mock_user
    db_session_mock.get.return_value = mock_user
    db_session_mock.query().all.return_value = [mock_payment]
    response = client.get(f'/api/v1/transactions/user/{mock_user.id}')
    assert response.status_code == 200
    


