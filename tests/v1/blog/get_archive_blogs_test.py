from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.v1.models.blog import Blog
from api.v1.routes.blog import get_db

from main import app
@pytest.fixture
def mock_db_session():
    mock_db = MagicMock(spec=Session)
    return mock_db

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_get_archive_blogs(mock_db_session, monkeypatch):
    def override_get_db():
        return mock_db_session
    
    monkeypatch.setattr("api.v1.routes.blog.get_db", override_get_db)
    
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
    
    response = client.get("/blog/archive?limit=5&skip=0")
    
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert json_data["message"] == "Successfully fetched all archived blogs"
    assert isinstance(json_data["data"], list)


# def test_get_all_active_blogs(mock_db_session):
#     response = client.get("/api/v1/blogs/active") 
#     assert response.status_code == 200
#     assert response.json()["message"] == "Successfully fetched active blogs"
#     assert isinstance(response.json()["data"], list)



@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def client(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_get_archive_blogs(client, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []

    response = client.get("/api/v1/blogs/archive?limit=5&skip=0")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert json_data["message"] == "Successfully fetched all archived blogs"
    assert isinstance(json_data["data"]["items"], list)


from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.v1.routes.blog import get_db
from main import app

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def client(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_get_all_active_blogs(client, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []

    response = client.get("/api/v1/blogs/active")

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully fetched active blogs"
    assert isinstance(response.json()["data"]["items"], list)