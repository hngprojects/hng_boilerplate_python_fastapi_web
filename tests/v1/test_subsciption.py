import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.utils.auth import hash_password
from api.db.database import Base, get_db
from api.v1.models.user import User
from api.v1.models.base import Base
from api.v1.models.subscription import Subscription

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

# Create tables in the test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

class TestUserSubscriptionCancellationConfirmation(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		# Set up a test user in the database
		db = TestingSessionLocal()
		test_user = User(
			username="testuser6",
			email="testuser6@example.com",
			password=hash_password("testpassword"),
			first_name="Test",
			last_name="User",
			is_active=True
		)
		new_subscription = Subscription(user=test_user, plan="Premium", is_active=False)
		db.add(new_subscription)
		db.add(test_user)
		db.commit()
		db.refresh(test_user)
		db.refresh(new_subscription)
		db.close()
	
	def test_subscription_cancellation_confirmation(self):
		db = TestingSessionLocal()
		response = client.post("/api/v1/auth/login", json={
			"username": "testuser6",
			"password": "testpassword"
		})
		self.assertEqual(response.status_code, 200)
		sub = db.query(Subscription).first()
		login_token = response.json()['access_token']
		response = client.post(f"/api/v1/user/subscription/notification/cancellation/{sub.id}",
							   headers={"Authorization": f"Bearer {login_token}"})
		db.commit()
		db.close()
		self.assertEqual(response.status_code, 200)
	
		sub = {"id": "yuut nuuun 7787 7fd"}
		response = client.post(f"/api/v1/user/subscription/notification/cancellation/{sub['id']}",
								headers={"Authorization": f"Bearer {login_token}"})
		self.assertEqual(response.status_code, 400)

	def tearDown(self):
		Base.metadata.drop_all(bind=engine)




if __name__ == "__main__":
	unittest.main()