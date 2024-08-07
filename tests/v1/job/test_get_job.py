import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from unittest.mock import MagicMock
from api.v1.models.job import Job
from datetime import datetime
from faker import Faker

fake = Faker()
client = TestClient(app)

# Sample job data
sample_job_data = Job(
    id="1",  # Ensure the ID is a string
    author_id=fake.uuid4(),
    title=fake.job(),
    description=fake.paragraph(),
    department=fake.random_element(["Engineering", "Marketing", "Sales"]),
    location=fake.city(),
    salary=fake.random_element(["$60,000 - $80,000", "$80,000 - $100,000"]),
    job_type=fake.random_element(["Full-time", "Contract", "Part-time"]),
    company_name=fake.company(),
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow(),
)

# Mocking the database
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield
    
    # Clean up after the test by removing the override
    app.dependency_overrides = {}

# Test for valid job retrieval
def test_get_job_valid_id(db_session_mock):
    # Set up the mock query to return the sample job
    db_session_mock.query().filter().first.return_value = sample_job_data
    
    response = client.get(f"/api/v1/jobs/{sample_job_data.id}")
    
    assert response.status_code == 200
    assert response.json()['message'] == "Retrieved Job successfully"
    assert response.json()['success'] == True
