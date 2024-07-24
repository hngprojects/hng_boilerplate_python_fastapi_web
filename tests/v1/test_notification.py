import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.base import Base
from api.v1.services.user import user_service
from api.v1.models.notifications import Notification

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


def test_mark_notification_as_read(test_db):
    # Create test user

    user = User(
        username="testuser1",
        email="testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Create test notification

    notification = Notification(
        user_id=user.id,
        title="Test notification",
        message="This is my test notification message",
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)

    # get access token

    login = client.post(
        "api/v1/auth/login",
        data={"username": "testuser1", "password": "Testpassword@123"},
    )

    access_token = login.json()["data"]["access_token"]
    headers = {"authorization": f"Bearer {access_token}"}

    response = client.patch(f"/api/v1/notifications/{notification.id}", headers=headers)

    # clean up the database

    test_db.query(Notification).delete()
    test_db.query(User).delete()
    test_db.commit()
    test_db.close()

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["status_code"] == 200
    assert response.json()["message"] == "Notifcation marked as read"


def test_mark_notification_as_read_unauthenticated_user(test_db):
    # Create test user

    user = User(
        username="testuser1",
        email="testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Create test notification

    notification = Notification(
        user_id=user.id,
        title="Test notification",
        message="This is my test notification message",
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)

    response = client.patch(f"/api/v1/notifications/{notification.id}")

    # clean up the database

    test_db.query(Notification).delete()
    test_db.query(User).delete()
    test_db.commit()
    test_db.close()

    assert response.status_code == 401
    assert response.json()["success"] == False
    assert response.json()["status_code"] == 401
