import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.utils.auth import hash_password
from api.db.database import Base, get_db
from api.v1.models.user import User
from api.v1.models.base import Base
from api.v1.models.subscription import Subscription

test_db_name = 'dbtest' # put your test db name
test_db_pw = '2445Bami**' # put your test db pw
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://hng:{test_db_pw}@localhost:5432/{test_db_name}"
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
def db():
	db = TestingSessionLocal()
	yield db
	db.close()

def create_test_user(db):
	user = User(
			username="testuser9",
			email="testuser9@example.com",
			password=hash_password("testpassword"),
			first_name="Test",
			last_name="User",
			is_active=True
		)
	db.add(user)
	db.commit()
	db.refresh(user)
	db.close()
	subscription = Subscription(user=user, plan="Premium", is_active=False)
	db.add(subscription)
	db.commit()
	db.refresh(subscription)
	# return subscription

def test_subscription_cancellation_confirmation(db):
	create_test_user(db)
	
	response = client.post("/api/v1/auth/login", json={
		"username": "testuser9",
		"password": "testpassword"
	})
	assert response.status_code == 200
	sub = db.query(Subscription).first()
	login_token = response.json()['access_token']
	response = client.post(f"/api/v1/user/subscription/notification/cancellation/{sub.id}",
							headers={"Authorization": f"Bearer {login_token}"})
	db.commit()
	db.close()
	assert response.status_code ==  200

	sub = {"id": "yuut nuuun 7787 7fd"}
	response = client.post(f"/api/v1/user/subscription/notification/cancellation/{sub['id']}",
							headers={"Authorization": f"Bearer {login_token}"})
	assert response.status_code == 400

