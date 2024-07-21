import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from main import app
from api.v1.models.testimonial import Testimonial
from sqlalchemy.ext.declarative import declarative_base
from api.v1.models.user import User
from dotenv import load_dotenv
from api.utils.auth import create_access_token, hash_password
from uuid_extensions import uuid7
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
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password=hashed_password,
        first_name="Admin",
        last_name="User",
        is_admin=True,
        is_active=True,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    token_expires = timedelta(minutes=30)
    admin_token = create_access_token(
        data={"username": admin_user.username}, expires_delta=token_expires
    )

    testimonial = Testimonial(
        firstname="John", lastname="Doe", content="Hello WOrld", user_id=admin_user.id
    )
    db.add(testimonial)
    db.commit()
    db.refresh(testimonial)

    # Define a finalizer function for teardown
    def finalizer():
        print("\nPerforming teardown...")
        db.query(Testimonial).delete()
        db.query(User).delete()
        db.commit()
        db.close()
        # Clean up any resources if needed

    # Register the finalizer to ensure cleanup
    request.addfinalizer(finalizer)

    return {
        "admin_user": admin_user,
        "testimonial": testimonial,
        "admin_token": admin_token,
    }


def test_delete_existing_testimonial(
    client: TestClient, setup: dict[str, User | Testimonial | str]
):
    testimonial = setup["testimonial"]
    admin_token = setup["admin_token"]

    response = client.delete(
        f"/api/v1/testimonials/{testimonial.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Testimonial deleted successfully",
        "status_code": 200,
    }


def test_delete_non_existent_testimonial(
    client: TestClient, setup: dict[str, User | Testimonial | str]
):
    non_existent_id = uuid7()
    admin_token = setup["admin_token"]
    response = client.delete(
        f"/api/v1/testimonials/{non_existent_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Testimonial not found"}


def test_delete_testimonial_without_authentication(
    client: TestClient, setup: dict[str, User | Testimonial | str]
):
    testimonial = setup["testimonial"]
    response = client.delete(f"/api/v1/testimonials/{testimonial.id}")

    assert response.status_code == 401
