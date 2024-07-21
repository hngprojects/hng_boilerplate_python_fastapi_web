import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...main import app
from api.db.database import Base, get_db
from api.v1.models.job import Job


client = TestClient(app)


@pytest.fixture
def db_session_mock(mocker):
    db_session = mocker.MagicMock()
    yield db_session


@pytest.fixture(autouse=True)
def override_get_db(mocker, db_session_mock):
    mocker.patch("app.v1.routes.job.get_db", return_value=db_session_mock)


client = TestClient(app)


@pytest.fixture
def mock_db(mocker):
    return mocker.patch("main.fake_jobs_db", [])


def test_create_job(mock_db):
    db_session_mock.query(Job).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser1", "password": "testpassword"},
        )

        # Request headers

    headers = {"Authorization": f"Bearer {login_response.json().get("access_token")}"}

    data = {
        "title": "test job",
        "description": "This is my test job",
        "location": "UK",
        "job_type": "Frontend developer",
        "salary": 50000,
        "company_name": "Tech hub.ltd",
    }

    response = client.post("/api/v1/jobs", data=data, headers=headers)
    assert response.status_code == 201
    assert response.json() == data
    assert len(mock_db) == 1
    assert mock_db[0] == data

if __name__ == "__main__":
    pytest.main()
