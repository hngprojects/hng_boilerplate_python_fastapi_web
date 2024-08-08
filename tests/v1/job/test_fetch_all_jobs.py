import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from unittest.mock import MagicMock
from api.v1.models.job import Job
from faker import Faker

fake = Faker()
client = TestClient(app)


data = [ 
    	Job(
            author_id=fake.uuid4(),
            title=fake.job(),
            description=fake.paragraph(),
            department=fake.random_element(["Engineering", "Marketing", "Sales"]),
            location=fake.city(),
            salary=fake.random_element(["$60,000 - $80,000", "$80,000 - $100,000"]),
            job_type=fake.random_element(["Full-time", "Contract", "Part-time"]),
            company_name=fake.company(),
        ) for job in range(10)
    ]


"""Mocking The database"""
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

"""Testing the database"""
def test_get_jobs(db_session_mock):
	db_session_mock.query().offset().limit().all.return_value = data

	url = 'api/v1/jobs'
	mock_query = MagicMock()
	db_session_mock.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = data

	db_session_mock.query.return_value = mock_query
	response = client.get(url)
	print(response.json()['data'])
	assert response.status_code == 200
