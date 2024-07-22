import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from api.db.database import get_db, get_db_engine, Base
from main import app
from api.v1.models.plans import SubscriptionPlan

# Configure test database by setting database to test mode to true
engine = get_db_engine(test_mode=True)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_create_subscription_plan(client, db):
    response = client.post(
        "/api/v1/plans",
        headers={"Authorization": "Bearer admin-token"},
        json={
            "name": "Basic Plan",
            "description": "This is a basic subscription plan.",
            "price": 1000,
            "duration": "30 days",
            "features": ["Feature 1", "Feature 2"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Basic Plan"
    assert data["description"] == "This is a basic subscription plan."
    assert data["price"] == 1000
    assert data["duration"] == "30 days"
    assert data["features"] == ["Feature 1", "Feature 2"]

def test_create_subscription_plan_duplicate_name(client, db):
    # Create the first plan
    response = client.post(
        "/api/v1/plans",
        headers={"Authorization": "Bearer admin-token"},
        json={
            "name": "Premium Plan",
            "description": "This is a premium subscription plan.",
            "price": 5000,
            "duration": "1 month",
            "features": ["Feature 1", "Feature 2"],
        },
    )
    assert response.status_code == 201

    # Attempt to create a plan with an existing plan name
    response = client.post(
        "/api/v1/plans",
        headers={"Authorization": "Bearer admin-token"},
        json={
            "name": "Premium Plan",
            "description": "This is a duplicate plan name.",
            "price": 5000,
            "duration": "1 months",
            "features": ["Feature 1", "Feature 2"],
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Subscription plan already exists."}

def test_create_subscription_plan_unauthorized(client, db):
    response = client.post(
        "/api/v1/plans",
        headers={"Authorization": "Bearer invalid-token"},
        json={
            "name": "Unauthorized Plan",
            "description": "This should not be created.",
            "price": 1500,
            "duration": "1 year",
            "features": ["Feature 3", "Feature 4"],
        },
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "User is not authorized to create subscription plans."}
