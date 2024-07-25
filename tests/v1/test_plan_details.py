import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.db.database import get_db
from api.core.dependencies.auth import create_test_user, get_user_token

client = TestClient(app)

@pytest.fixture(scope='module')
def test_db():
    from api.db.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope='module')
def token(test_db):
    return get_user_token(test_db)

def test_get_billing_plan_details(test_db, token):
    # Create test data
    organization_id = "12345"
    plan_name = "premium"
    
    test_db.add(BillingPlan(
        organization_id=organization_id,
        name=plan_name,
        price=20.00,
        currency="USD",
        features=["Feature 1", "Feature 2", "Feature 3"],
        description="Detailed description of the Premium Plan."
    ))
    test_db.commit()
    
    response = client.get(
        f"/api/v1/organizations/{organization_id}/billing-plans/{plan_name}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json() == {
        "id": "premium",
        "name": "Premium Plan",
        "price": 20.00,
        "features": ["Feature 1", "Feature 2", "Feature 3"],
        "description": "Detailed description of the Premium Plan."
    }

def test_get_billing_plan_details_not_found(test_db, token):
    organization_id = "12345"
    plan_name = "non_existent_plan"
    
    response = client.get(
        f"/api/v1/organizations/{organization_id}/billing-plans/{plan_name}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Billing plan not found"}

