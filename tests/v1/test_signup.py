import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.utils.auth import hash_password
from api.db.database import Base, get_db
from api.v1.models.user import User, WaitlistUser
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.base import Base
from api.v1.models.subscription import Subscription
from api.v1.models.blog import Blog
from api.v1.models.job import Job
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission
test_db_name = 'test_db'
test_db_pw = 'root'
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:{test_db_pw}@localhost:5432/{test_db_name}"
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

class TestUserCreation(unittest.TestCase):
    
    def test_create_user(self):
        response = client.post("/api/v1/auth/register", json={"username": "testuser", "email": "testuser@example.com", "password": "tesAtpa@142ssword", "first_name": "Test", "last_name": "User", "is_active": True})
        self.assertEqual(response.status_code, 201)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)


class TestUserCreation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up a test user in the database
        db = TestingSessionLocal()
        test_user = User(
            username="testuser1",
            email="testuser1@example.com",
            password=hash_password("testpassword"),
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.close()
    
    def test_create_user(self):
        response = client.post("/api/v1/auth/register", json={"username": "testuser", "email": "testuser@example.com", "password": "tesAtpa@142ssword", "first_name": "Test", "last_name": "User", "is_active": True})
        self.assertEqual(response.status_code, 201)
    
    def test_create_user(self):
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser1",
            "password": "testpassword"
            })
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    unittest.main()