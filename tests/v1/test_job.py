# import sys, os


# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from main import app
from api.db.database import Base, get_db
from api.utils.auth import hash_password
from api.v1.models.user import User
from api.v1.models.base import Base
from api.v1.models.job import Job

SQLALCHEMY_DATABASE_URL = config("DB_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()


def create_user(test_db):

    # Add user to database
    user = User(
        username="testuser",
        email="testuser@gmail.com",
        password=hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_admin=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)


def test_create_job_success(test_db):
    user = User(
        username="testuser1",
        email="testuser1@gmail.com",
        password=hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=False,
        is_admin=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    login = client.post(
        "/auth/login", data={"username": "testuser1", "password": "Testpassword@123"}
    )


    access_token = login.json()["access_token"]
    headers = {"authorization": f"Bearer {access_token}"}

    data = {
        "title": "first job",
        "description": "This is my first job",
        "location": "Sokoto",
        "job_type": "Frontend developer",
        "salary": 50000,
        "company_name": "Dev endgine technology",
    }


    response = client.post("/api/v1/jobs", headers=headers, json=data)

    # clean up the database

    test_db.query(Job).delete()
    test_db.query(User).delete()
    test_db.commit()
    test_db.close()

    assert response.status_code == 201
def test_create_job_bad_request(test_db):
    user = User(
        username="testuser1",
        email="testuser1@gmail.com",
        password=hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=False,
        is_admin=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    login = client.post(
        "/auth/login", data={"username": "testuser1", "password": "Testpassword@123"}
    )


    access_token = login.json()["access_token"]
    headers = {"authorization": f"Bearer {access_token}"}

    data = {
        "location": "Sokoto",
        "job_type": "Frontend developer",
        "salary": 50000,
        "company_name": "Dev endgine technology",
    }


    response = client.post("/api/v1/jobs", headers=headers, json=data)

    # clean up the database

    test_db.query(Job).delete()
    test_db.query(User).delete()
    test_db.commit()
    test_db.close()

    assert response.status_code == 422

def test_create_job_by_unauthenticated_user(test_db):
    data = {
        "title": "first job",
        "description": "This is my first job",
        "location": "Sokoto",
        "job_type": "Frontend developer",
        "salary": 50000,
        "company_name": "Dev endgine technology",
    }


    response = client.post("/api/v1/jobs", json=data)

    # clean up the database

    test_db.query(Job).delete()
    test_db.query(User).delete()
    test_db.commit()
    test_db.close()

    assert response.status_code == 401