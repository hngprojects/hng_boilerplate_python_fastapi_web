from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.organisation import Organisation
from api.v1.services.user import user_service
from api.v1.services.billing_plan import billing_plan_service
from api.v1.models.user import User
from api.v1.models.billing_plan import BillingPlan
from main import app



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


def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email="test@gmail.com",
        password=user_service.hash_password("Testuser@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_org():
    return Organisation(
        id=str(uuid7()),
        name="Test Organisation",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_billing_plan():
    return BillingPlan(
        id=str(uuid7()), 
        organisation_id=mock_org().id,  
        name="Premium Plan",
        price=49.99,
        currency="NGN",  # Currency code
        duration="yearly",  # Duration of the plan
        description="This is a premium billing plan with extra features.",
        features=["Feature 1", "Feature 2", "Feature 3"],
        updated_at=datetime.now(timezone.utc)
    )

def test_get_plan_unauthorized(client, db_session_mock):
    '''Test for unauthorized user'''    

    mock_plan_instance = mock_billing_plan()


    with patch("api.v1.services.billing_plan.BillingPlanService.fetch", return_value=mock_plan_instance) as mock_fetch:

        response = client.get(f'/api/v1/organisations/billing-plans/{mock_plan_instance.id}')

        assert response.status_code == 401
