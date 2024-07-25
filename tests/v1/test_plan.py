import pytest
from fastapi.testclient import TestClient
from ...main import app
from api.db.database import get_db
from sqlalchemy.orm import Session

client = TestClient(app)

def test_get_billing_plan_details(client: TestClient, db: Session):
    # Setup: Create a test billing plan in the database
    organization_id = "12345"
    plan_name = "premium"
    db.execute("""
        INSERT INTO billing_plans (organization_id, name, price, currency, features)
        VALUES (:organization_id, :name, :price, :currency, :features)
    """, {
        "organization_id": organization_id,
        "name": plan_name,
        "price": 20.00,
        "currency": "USD",
        "features": ["Feature 1", "Feature 2", "Feature 3"]
    })
    db.commit()

    response = client.get(f"/api/v1/organizations/{organization_id}/billing-plans/{plan_name}", headers={"Authorization": "Bearer <token>"})

    assert response.status_code == 200
    assert response.json() == {
        "status": 200,
        "message": "details fetched successfully",
        "data": {
            "plan": {
                "id": "premium",
                "name": "Premium Plan",
                "price": 20.00,
                "features": ["Feature 1", "Feature 2", "Feature 3"],
                "description": "Detailed description of the Premium Plan."
            }
        }
    }

def test_get_billing_plan_details_unauthorized(client: TestClient):
    organization_id = "12345"
    plan_name = "premium"
    response = client.get(f"/api/v1/organizations/{organization_id}/billing-plans/{plan_name}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
