import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta
from api.v1.models.payment import Payment
from api.v1.models.user import User
from api.v1.services.user import user_service

from ...main import app
from api.v1.models.blog import Blog
from api.v1.routes.blog import get_db

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

def create_mock_user(mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=str(uuid7()),
        username="testuser",
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_super_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    return mock_user

def create_mock_payment(mock_db_session, user_id):
    """Create a mock user in the mock database session."""
    mock_payment = Payment(
        id=str(uuid7()),
        amount=5000,
        currency='NGN',
        status='pending',
        method='credit card',
        transaction_id='c6842ef66071455645e107479c28674b',
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_payment

    return mock_payment

def test_post_payment(client, db_session_mock):
    """Create a mock user in the mock database session."""
    create_mock_user(db_session_mock)
    token = user_service.create_access_token(user_id=str(uuid7()))

    response = client.post("/api/v1/payments/create", headers={
        "Authorization": f"Bearer {token}"
    }, json={
        "amount": "5000",
        "currency": "NGN",
        "status": "pending",
        "method": "credit card",
        "transaction_id": "c6842ef66071455645e107479c28674b"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Payment successfully created"

