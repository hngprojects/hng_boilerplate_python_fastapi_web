import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from main import app
from api.v1.models.user import User
from api.utils.auth import hash_password

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:{test_db_pw}@localhost:5432/{test_db_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_client():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def create_test_user():
    db = TestingSessionLocal()
    password_hashed = hash_password("testpassword")
    test_user = User(
        username="testuser",
        email="testuser@example.com",
        password=password_hashed,
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    yield test_user
    db.close()

def get_auth_token(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_get_summary(test_client, create_test_user):
    token = get_auth_token(test_client, "testuser", "testpassword")
    response = test_client.get("/api/v1/analytics/summary", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["status"] is True

def test_get_line_chart_data(test_client, create_test_user):
    token = get_auth_token(test_client, "testuser", "testpassword")
    response = test_client.get("/api/v1/analytics/line-chart-data", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["status"] is True

def test_get_bar_chart_data(test_client, create_test_user):
    token = get_auth_token(test_client, "testuser", "testpassword")
    response = test_client.get("/api/v1/analytics/bar-chart-data", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["status"] is True

def test_get_pie_chart_data(test_client, create_test_user):
    token = get_auth_token(test_client, "testuser", "testpassword")
    response = test_client.get("/api/v1/analytics/pie-chart-data", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["status"] is True
