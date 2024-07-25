import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ...main import app
from api.db.database import Base, get_db
from api.v1.models.billing_plan import BillingPlan

# Configure test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test client
client = TestClient(app)

# Create test database tables
Base.metadata.create_all(bind=engine)

# Override get_db dependency to use test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Helper function to create a billing plan in the test database
def create_test_billing_plan(db: Session, organization: str, plan_name: str):
    billing_plan = BillingPlan(
        organization_id=organization,
        name=plan_name,
        price=20.00,
        currency="USD",
        features=["Feature 1", "Feature 2", "Feature 3"]
    )
    db.add(billing_plan)
    db.commit()
    db.refresh(billing_plan)
    return billing_plan

@pytest.fixture(scope="module")
def setup_database():
    # Setup database and insert test data
    db = TestingSessionLocal()
    create_test_billing_plan(db, "12345", "premium")
    yield
    # Teardown database
    Base.metadata.drop_all(bind=engine)

def test_get_billing_plan_details(setup_database):
    organization = "12345"
    plan_name = "premium"
    response = client.get(f"/plans/organizations/{organization}/billing-plans/{plan_name}", headers={"Authorization": "Bearer <token>"})

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "details fetched successfully"
    assert response.json()["data"]["plan"]["name"] == "premium"
    assert response.json()["data"]["plan"]["price"] == 20.00
    assert response.json()["data"]["plan"]["features"] == ["Feature 1", "Feature 2", "Feature 3"]

def test_get_billing_plan_details_unauthorized():
    organization = "12345"
    plan_name = "premium"
    response = client.get(f"/plans/organizations/{organization}/billing-plans/{plan_name}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
