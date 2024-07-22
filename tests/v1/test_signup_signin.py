import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.utils.auth import hash_password
from api.db.database import Base, get_db
from api.v1.models.user import User
import random
from decouple import config

n = random.randint(1, 400)
SQLALCHEMY_DATABASE_URL = config("DB_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_get_db
# Create tables in the test database
Base.metadata.create_all(bind=engine)
client = TestClient(app)
@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()
n = random.randint(1, 405)
@pytest.fixture(scope="module")
def create_test_user(test_db):
    test_user = User(
        username=f"testuser{n}",
        email=f"testuser{n}@example.com",
        password=hash_password("testpassword"),
        first_name="Test",
        last_name="User",
        is_active=True
    )
    test_db.add(test_user)
    test_db.commit()
    return test_user
b = random.randint(1, 500)
def test_create_user(setup_database):
    response = client.post("/api/v1/auth/register", json={"username": f"testuser{b}", "email": f"testuser{b}@example.com", "password": "tesAtpa@142ssword", "first_name": "Test", "last_name": "User"})
    print(response.json().get('detail'))
    assert response.status_code == 201
