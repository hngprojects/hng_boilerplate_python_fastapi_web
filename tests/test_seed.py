import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from main import app
from api.db.database import get_db, Base

# PostgreSQL connection string for your test database.
SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost:5432/test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reset_test_schema(engine, schema_name="test_schema"):
    with engine.connect() as connection:
        connection.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
        connection.execute(text(f"CREATE SCHEMA {schema_name}"))
        connection.execute(text(f"SET search_path TO {schema_name}"))
        connection.commit()

reset_test_schema(engine, schema_name="test_schema")

# Ensure that the Base metadata uses the test schema.
Base.metadata.schema = "test_schema"
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_seed_endpoint():
    response = client.post("/api/v1/seed", params={"num_users": 2})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert data["status_code"] == 200
    assert data["message"].startswith("2 users and organizations seeded successfully.")
    assert len(data["data"]["users"]) == 2

def test_seed_endpoint_non_integer_num_users():
    response = client.post("/api/v1/seed", params={"num_users": "abc"})
    assert response.status_code == 422, response.text

def test_seed_endpoint_no_num_users():
    response = client.post("/api/v1/seed")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert data["status_code"] == 200
    assert data["message"].startswith("1 users and organizations seeded successfully.")
    assert len(data["data"]["users"]) == 1

def test_seed_endpoint_large_num_users():
    response = client.post("/api/v1/seed", params={"num_users": 100})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert data["status_code"] == 200
    assert data["message"].startswith("100 users and organizations seeded successfully.")
    assert len(data["data"]["users"]) == 100
