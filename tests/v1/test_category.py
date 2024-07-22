import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from decouple import config

from main import app
from api.db.database import Base, get_db
from api.utils.auth import hash_password
from api.v1.models.user import User
from api.v1.models.blog import BlogCategory

SQLALCHEMY_DATABASE_URL = config('DB_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Create tables in the test database
Base.metadata.create_all(bind=engine)

# Fixture to create a superadmin user
@pytest.fixture(scope="module")
def superadmin_user():
    db = TestingSessionLocal()
    hashed_password = hash_password("supersecurepassword")
    user = User(username="superadmin", password=hashed_password, role="superadmin")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

# Utility function to get auth token
def get_auth_token(client: TestClient, username: str, password: str):
    response = client.post("/api/v1/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]

# Test case: Successful category creation
def test_create_blog_category_success(superadmin_user):
    token = get_auth_token(client, "superadmin", "supersecurepassword")
    response = client.post(
        "/api/v1/blog-categories",
        json={"name": "Tech"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Blog category created successfully.",
        "data": {"name": "Tech"},
        "status_code": 201
    }

# Test case: Forbidden access for non-superadmin
def test_create_blog_category_forbidden(client: TestClient):
    # Create a regular user
    db = TestingSessionLocal()
    hashed_password = hash_password("userpassword")
    user = User(
        username="regularuser",
        password=hashed_password,
        role="user"
    )
    db.add(user)
    db.commit()
    db.close()
    
    token = get_auth_token(client, "regularuser", "userpassword")
    response = client.post(
        "/api/v1/blog-categories",
        json={"name": "Tech"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json() == {
        "status": "error",
        "message": "Forbidden. You do not have permission to create blog categories.",
        "status_code": 403
    }

# Test case: Unauthorized access
def test_create_blog_category_unauthorized():
    response = client.post("/api/v1/blog-categories", json={"name": "Tech"})
    assert response.status_code == 401
    assert response.json() == {
        "status": "error",
        "message": "Unauthorized. Token is missing or invalid.",
        "status_code": 401
    }

# Test case: Validation error for missing category name
def test_create_blog_category_validation_error(superadmin_user):
    token = get_auth_token(client, "superadmin", "supersecurepassword")
    response = client.post(
        "/api/v1/blog-categories",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "status": "error",
        "message": "Invalid request data. Please provide a valid category name.",
        "status_code": 400
    }