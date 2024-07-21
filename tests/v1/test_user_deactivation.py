import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.utils.auth import hash_password
from api.db.database import Base, get_db
from api.v1.models.user import User
from api.v1.models.base import Base

test_db_name = 'test_fastapi_db' # put your test db name
test_db_pw = 'postgres' # put your test db pw
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

class TestUserDeactivation(unittest.TestCase):

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
    
    def test_login(self):
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser1",
            "password": "testpassword"
        })
        self.assertEqual(response.status_code, 200)

        return response.json()['access_token']
    
    def test_deactivate_user_unauthorized(self):
        access_token = self.test_login()
        
        response = client.patch(
            "/api/v1/accounts/deactivate", 
            json={
                "reason": "No longer need the account",
                "confirmation": True
            }
        )
        self.assertEqual(response.status_code, 401)


    def test_deactivate_user_missing_field(self):
        access_token = self.test_login()
        
        response = client.patch(
            "/api/v1/accounts/deactivate", 
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "reason": "No longer need the account",
            }
        )
        self.assertEqual(response.status_code, 422)
    
    def test_deactivate_user_confirmation_false(self):
        access_token = self.test_login()
        
        response = client.patch(
            "/api/v1/accounts/deactivate", 
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "reason": "No longer need the account",
                "confirmation": False
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_deactivate_user(self):
        access_token = self.test_login()
        
        response = client.patch(
            "/api/v1/accounts/deactivate", 
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "reaspn": "No longer need the account",
                "confirmation": True
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_deactivate_user_user_inactive(self):
        access_token = self.test_login()
        
        response = client.patch(
            "/api/v1/accounts/deactivate", 
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "reaspn": "No longer need the account",
                "confirmation": True
            }
        )
        self.assertEqual(response.status_code, 400)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)
