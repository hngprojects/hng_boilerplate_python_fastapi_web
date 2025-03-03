import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from api.v1.models.job import Job
from faker import Faker

fake = Faker()
client = TestClient(app)

class FakeJob:
    def __init__(self, title, location, job_type):
        self.title = title
        self.location = location
        self.job_type = job_type
    def dict(self):
        return {"title": self.title, "location": self.location, "job_type": self.job_type}

class FakeQuery:
    def __init__(self, jobs):
        self.jobs = jobs
    def filter(self, predicate):
        filtered = list(filter(predicate, self.jobs))
        return FakeQuery(filtered)
    def all(self):
        return self.jobs

class FakeSession:
    def __init__(self, jobs):
        self.jobs = jobs
    def query(self, model):
        return FakeQuery(self.jobs)

class FakeColumn:
    def __init__(self, attr_name):
        self.attr_name = attr_name
    def ilike(self, pattern):
        def predicate(job):
            value = getattr(job, self.attr_name, "")
            return pattern.strip("%").lower() in value.lower()
        return predicate
    def __eq__(self, other):
        def predicate(job):
            return getattr(job, self.attr_name, None) == other
        return predicate

Job.title = FakeColumn("title")
Job.location = FakeColumn("location")
Job.job_type = FakeColumn("job_type")

fake_jobs = [
    FakeJob("Software Engineer", "New York", "Full Time"),
    FakeJob("Data Scientist", "San Francisco", "Part Time"),
    FakeJob("Backend Developer", "New York", "Contract")
]

@pytest.fixture
def fake_db():
    yield FakeSession(fake_jobs)

@pytest.fixture(autouse=True)
def override_get_db(fake_db):
    def get_db_override():
        yield fake_db
    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}

def test_filter_no_parameters():
    response = client.get("/api/v1/jobs/filter")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status_code"] == 200
    assert len(json_data["data"]) == 3
    assert json_data["message"] == "Successfully retrieved 3 jobs"

def test_filter_by_title():
    response = client.get("/api/v1/jobs/filter", params={"title": "Software"})
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["title"] == "Software Engineer"
    assert json_data["message"] == "Successfully retrieved 1 jobs"

def test_filter_by_location():
    response = client.get("/api/v1/jobs/filter", params={"location": "New York"})
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["data"]) == 2
    titles = [job["title"] for job in json_data["data"]]
    assert "Software Engineer" in titles
    assert "Backend Developer" in titles
    assert json_data["message"] == "Successfully retrieved 2 jobs"

def test_filter_by_job_type():
    response = client.get("/api/v1/jobs/filter", params={"job_type": "Part Time"})
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["job_type"] == "Part Time"
    assert json_data["message"] == "Successfully retrieved 1 jobs"

def test_filter_by_multiple_parameters():
    response = client.get("/api/v1/jobs/filter", params={"title": "Developer", "location": "New York"})
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["title"] == "Backend Developer"
    assert json_data["data"][0]["location"] == "New York"
    assert json_data["message"] == "Successfully retrieved 1 jobs"

def test_filter_no_match():
    response = client.get("/api/v1/jobs/filter", params={"title": "Manager"})
    assert response.status_code == 404
    json_data = response.json()
    assert json_data["message"] == "No jobs found matching the search parameters."
