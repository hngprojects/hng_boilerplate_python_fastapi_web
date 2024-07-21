import unittest
import uuid
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from main import app
from api.v1.models.customer import Customer
from api.v1.models.user import User
from dotenv import load_dotenv
import os
from api.utils.auth import create_access_token, hash_password

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://ahmed:01029371843@127.0.0.1:5432/hng_fast_api"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestDeleteCustomer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = TestingSessionLocal()
        hashed_password = hash_password("adminpassword")
        cls.admin_user = User(
            username="admin",
            email="admin@example.com",
            password=hashed_password,
            first_name="Admin",
            last_name="User",
            is_admin=True,
            is_active=True,
        )
        cls.db.add(cls.admin_user)
        cls.db.commit()
        cls.db.refresh(cls.admin_user)
        
        token_expires = timedelta(minutes=30)
        cls.admin_token = create_access_token(data={"sub": cls.admin_user.username}, expires_delta=token_expires)
        
        cls.customer = Customer(
            id=uuid.uuid4(),
            username="testcustomer",
            email="testcustomer@example.com",
            password="password",
            first_name="Test",
            last_name="Customer",
            is_deleted=False,
        )
        cls.db.add(cls.customer)
        cls.db.commit()
        cls.db.refresh(cls.customer)

    @classmethod
    def tearDownClass(cls):
        cls.db.query(User).delete()
        cls.db.query(Customer).delete()
        cls.db.commit()
        cls.db.close()

    def test_delete_customer_success(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.delete(f"/api/v1/customers/{self.customer.id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_deleted"])

    def test_delete_customer_not_found(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.delete(f"/api/v1/customers/{uuid.uuid4()}", headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Customer not found")

    def test_delete_customer_unauthorized(self):
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.delete(f"/api/v1/customers/{self.customer.id}", headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Unauthorized to perform this action")

    def test_delete_customer_already_deleted(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # First delete
        response = client.delete(f"/api/v1/customers/{self.customer.id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Try to delete again
        response = client.delete(f"/api/v1/customers/{self.customer.id}", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Customer already deleted")

    def test_delete_customer_database_error(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Simulate database error
        original_commit = TestingSessionLocal.commit
        def mock_commit():
            raise Exception("Mocked database error")
        TestingSessionLocal.commit = mock_commit
        
        response = client.delete(f"/api/v1/customers/{self.customer.id}", headers=headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Database error occurred")
        
        # Restore original commit
        TestingSessionLocal.commit = original_commit

if __name__ == '__main__':
    unittest.main()
