import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.utils.auth import hash_password
from api.v1.models.plans import SubscriptionPlan

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    db_session = next(get_db())
    yield db_session
    db_session.close()

# Create a test admin user
def create_test_admin_user(db: Session):
    admin_user = User(
        username="testadmin",
        email="testadmin@example.com",
        hashed_password=hash_password("testpassword"),
        is_active=True,
        is_admin=True  
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user

# Generate token for the test admin user
def get_admin_token():
    response = client.post(
        "/auth/login",
        data={
            "username": "testadmin",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token


@pytest.fixture(scope="module", autouse=True)
def setup_admin_user(db: Session):
    create_test_admin_user(db)

# Test creating a subscription plan
def test_create_subscription_plan(db: Session):
    token = get_admin_token()
    
    response = client.post(
        "/api/v1/plans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Basic Plan",
            "description": "This is a basic subscription plan.",
            "price": 1000,
            "duration": "30 days",
            "features": ["Feature 1", "Feature 2"],
        },
    )
    assert response.status_code == 201

# Test creating a subscription plan with a duplicate name
def test_create_subscription_plan_duplicate_name(db: Session):
    token = get_admin_token()
    
    # Create the first plan
    response = client.post(
        "/api/v1/plans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Premium Plan",
            "description": "This is a premium subscription plan.",
            "price": 5000,
            "duration": "1 month",
            "features": ["Feature 1", "Feature 2"],
        },
    )
    assert response.status_code == 201

    # Try to create a plan with the same name
    response = client.post(
        "/api/v1/plans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Premium Plan",
            "description": "This is another premium subscription plan.",
            "price": 6000,
            "duration": "1 month",
            "features": ["Feature 3", "Feature 4"],
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Subscription plan already exists."}

# Test unauthorized plan creation
def test_create_subscription_plan_unauthorized(db: Session):
    response = client.post(
        "/api/v1/plans",
        headers={"Authorization": "Bearer invalidtoken"},
        json={
            "name": "Unauthorized Plan",
            "description": "This should not be created.",
            "price": 1500,
            "duration": "1 year",
            "features": ["Feature 3", "Feature 4"],
        },
    )
    assert response.status_code == 403
