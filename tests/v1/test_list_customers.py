import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.utils.auth import hash_password, create_access_token
from api.db.database import Base, get_db
from api.v1.models.user import User
from datetime import timedelta

# Database configuration
test_db_name = '' # put your test db name
test_db_pw = '' # put your test db pw
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

Base.metadata.create_all(bind=engine)

client = TestClient(app)

class TestFetchCustomers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up test users in the database
        db = TestingSessionLocal()
        
        # Create first test user
        cls.user1 = User(
            username="testuser12",
            email="testuser12@example.com",
            password=hash_password("testpassword"),
            first_name="Test1",
            last_name="User1",
            is_active=True,
            is_admin=True
        )
        db.add(cls.user1)
        
        # Create second who is not an admin
        cls.user2 = User(
            username="testuser13",
            email="testuser13@example.com",
            password=hash_password("testpassword"),
            first_name="Test2",
            last_name="User2",
            is_active=True,
            is_admin=False
        )
        db.add(cls.user2)

        # Create third user who is not active
        cls.user3 = User(
            username="testuser14",
            email="testuser14@example.com",
            password=hash_password("testpassword"),
            first_name="Test2",
            last_name="User2",
            is_active=False,
            is_admin=True
        )
        db.add(cls.user3)

        # Create forth user who is not authenticated
        cls.user4 = User(
            username="testuser15",
            email="testuser15@example.com",
            password=hash_password("testpassword"),
            first_name="Test2",
            last_name="User2",
            is_active=False,
            is_admin=True
        )
        db.add(cls.user4)
        
        db.commit()
        db.close()

        # Generate access tokens for the test users
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        cls.access_token_user1 = create_access_token(
            data={"username": "testuser12"}, expires_delta=access_token_expires
        )
        
        cls.access_token_user2 = create_access_token(
            data={"username": "testuser13"}, expires_delta=access_token_expires
        )

        cls.access_token_user3 = create_access_token(
            data={"username": "testuser14"}, expires_delta=access_token_expires
        )

    def test_fetch_customers_user1(self):
        headers = {
            'Authorization': f'Bearer {self.access_token_user1}'
        }
        response = client.get("/api/v1/customers", headers=headers)
        self.assertEqual(response.status_code, 200)

    # Testing with User2 who is not an admin
    def test_fetch_customers_user2(self):
        headers = {
            'Authorization': f'Bearer {self.access_token_user2}'
        }
        response = client.get("/api/v1/customers", headers=headers)
        self.assertEqual(response.status_code, 401)

    # Testing with User3 who is not active
    def test_fetch_customers_user3(self):
        headers = {
            'Authorization': f'Bearer {self.access_token_user3}'
        }
        response = client.get("/api/v1/customers", headers=headers)
        self.assertEqual(response.status_code, 401)

    # Testing with unauthenticated User4
    def test_fetch_customers_user4(self):
        response = client.get("/api/v1/customers")
        self.assertEqual(response.status_code, 401)


    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    unittest.main()
