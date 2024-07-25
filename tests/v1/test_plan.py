import pytest
from fastapi.testclient import TestClient
from ...main import app
from api.db.database import SessionLocal
from api.v1.models.user import User
from api.v1.models.billing_plan import BillingPlan
from api.v1.services.user import user_service

client = TestClient(app)

@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture
def super_admin_user(db):
    user = User(id="test_user", is_super_admin=True)
    db.add(user)
    db.commit()
    yield user
    db.delete(user)
    db.commit()

@pytest.fixture
def regular_user(db):
    user = User(id="test_user2", is_super_admin=False)
    db.add(user)
    db.commit()
    yield user
    db.delete(user)
    db.commit()

@pytest.fixture
def billing_plan(db):
    billing_plan = BillingPlan(organization_id="12345", name="premium", price=20.00, currency="USD", features=["Feature 1", "Feature 2", "Feature 3"], description="Detailed description of the Premium Plan.")
    db.add(billing_plan)
    db.commit()
    yield billing_plan
    db.delete(billing_plan)
    db.commit()

def test_get_billing_plan_success(db, super_admin_user, billing_plan):
    # Mock the get_current_user function to return the test super admin user
    user_service.get_current_user = lambda db, token: super_admin_user

    response = client.get(f"/plans/12345/billing-plans/premium", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json() == {
        "id": str(billing_plan.id),
        "name": billing_plan.name,
        "description": billing_plan.description,
        "price": billing_plan.price,
        "duration": billing_plan.duration,
        "features": billing_plan.features
    }

def test_get_billing_plan_not_found(db, super_admin_user):
    # Mock the get_current_user function to return the test super admin user
    user_service.get_current_user = lambda db, token: super_admin_user

    response = client.get("/plans/12345/billing-plans/nonexistent", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Billing plan not found"}

def test_get_billing_plan_unauthorized(db, regular_user, billing_plan):
    # Mock the get_current_user function to return the test regular user
    user_service.get_current_user = lambda db, token: regular_user

    response = client.get(f"/plans/12345/billing-plans/premium", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have permission to access this resource"}
