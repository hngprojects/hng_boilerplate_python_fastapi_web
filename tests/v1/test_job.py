import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from main import app

from sqlalchemy.ext.declarative import declarative_base
from api.v1.models.user import User
from dotenv import load_dotenv
from api.utils.auth import create_access_token, hash_password
import pytest


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_TEST")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


# client = TestClient(app)


@pytest.fixture
def setup(request, session):
    print("\nSetting up resources...")
    db = session
    hashed_password = hash_password("adminpassword")
    user = User(
        username="admin",
        email="admin@example.com",
        password=hashed_password,
        first_name="Admin",
        last_name="User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token_expires = timedelta(minutes=30)
    token = create_access_token(
        data={"username": user.username}, expires_delta=token_expires
    )

    def finalizer():
        db.query(User).delete()
        db.commit()
        db.close()
        # Clean up any resources if needed

    # Register the finalizer to ensure cleanup
    request.addfinalizer(finalizer)


    return {
        "token": token,
    }


def test_create_job(client: TestClient, setup: dict[str, str]):
    headers = {"authorization": f"Bearer {setup['token']}"}

    data = {
        "title": "first job",
        "description": "This is my first job",
        "location": "Sokoto",
        "job_type": "Frontend developer",
        "salary": 50000,
        "company_name": "Dev endgine technology",
    }

    response = client.post("/api/v1/jobs", headers=headers, json=data)

    assert response.status_code == 201
