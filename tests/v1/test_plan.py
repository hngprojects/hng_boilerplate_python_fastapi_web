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

def create_test_admin_user(db: Session):
    admin_user = User(
        username="testadmin",
        email="testadmin@example.com",
        password=hash_password("testpassword"),
        is_active=True,
        is_admin=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user

def create_test_user(db: Session):
    test_user = User(
        username="testuser",
        email="testuser@email.com",
        password=hash_password("userpassword"),
        is_active=True,
        is_admin=False
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    return test_user

def get_token(username: str, password: str):
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token

@pytest.fixture(scope="module", autouse=True)
def setup_admin_user(db: Session):
    create_test_admin_user(db)

@pytest.fixture(scope="module", autouse=True)
def setup_test_user(db: Session):
    create_test_user(db)

def test_create_subscription_plan(db: Session):
    token = get_token("testadmin", "testpassword")
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

def test_create_subscription_plan_duplicate_name(db: Session):
    token = get_token("testadmin", "testpassword")
    
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

def test_create_subscription_plan_unauthorized(db: Session):
    token = get_token("testuser", "userpassword")
    response = client.post(
        "/api/v1/plans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Unauthorized Plan",
            "description": "This should not be created.",
            "price": 1500,
            "duration": "1 year",
            "features": ["Feature 3", "Feature 4"],
        },
    )
    assert response.status_code == 403
