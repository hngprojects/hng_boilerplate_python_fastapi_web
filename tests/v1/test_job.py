import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.utils.auth import hash_password
from api.db.database import Base, get_db
from api.v1.models.user import User
from api.v1.models.job import Job  # Import your Job model

test_db_name = ""  # put your test db name
test_db_pw = ""  # put your test db pw
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://postgres:{test_db_pw}@localhost:5432/{test_db_name}"
)
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


class TestJobEndpoints(unittest.TestCase):
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
            is_active=True,
        )
        db.add(test_user)
        db.commit()

        # Add some job listings
        job1 = Job(
            title="Job 1",
            description="Description for job 1",
            location="Location 1",
            job_type="Type 1",
            salary=40000,
            company_name="Company 1",
            user_id=test_user.id  # Assuming user_id is required
        )
        job2 = Job(
            title="Job 2",
            description="Description for job 2",
            location="Location 2",
            job_type="Type 2",
            salary=50000,
            company_name="Company 2",
            user_id=test_user.id
        )
        db.add(job1)
        db.add(job2)
        db.commit()
        db.close()

    def test_create_job(self):
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser1", "password": "testpassword"},
        )

        headers = {"Authorization": f"Bearer {login_response.json().get('access_token')}"}

        data = {
            "title": "test job",
            "description": "This is my test job",
            "location": "UK",
            "job_type": "Frontend developer",
            "salary": 50000,
            "company_name": "Tech hub.ltd",
        }

        response = client.post("/api/v1/jobs", json=data, headers=headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], 201)
        self.assertEqual(response.json()["message"], "Job listing created successfully")
        self.assertIsInstance(response.json(), dict)
        self.assertIsInstance(response.json()["data"], dict)
        self.assertIn("id", response.json()["data"])
        self.assertIn("description", response.json()["data"])
        self.assertIn("location", response.json()["data"])
        self.assertIn("job_type", response.json()["data"])
        self.assertIn("salary", response.json()["data"])
        self.assertIn("company_name", response.json()["data"])
        self.assertIn("created_at", response.json()["data"])

    def test_get_all_jobs(self):
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser1", "password": "testpassword"},
        )

        headers = {"Authorization": f"Bearer {login_response.json().get('access_token')}"}

        response = client.get("/api/v1/jobs", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], 200)
        self.assertEqual(response.json()["message"], "Job listings retrieved successfully")
        self.assertIsInstance(response.json(), dict)
        self.assertIsInstance(response.json()["data"], list)
        
        # Check if at least one job is returned
        self.assertGreater(len(response.json()["data"]), 0)

        # Additional checks to ensure job details are present
        for job in response.json()["data"]:
            self.assertIn("id", job)
            self.assertIn("title", job)
            self.assertIn("description", job)
            self.assertIn("location", job)
            self.assertIn("job_type", job)
            self.assertIn("salary", job)
            self.assertIn("company_name", job)
            self.assertIn("created_at", job)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    unittest.main()
