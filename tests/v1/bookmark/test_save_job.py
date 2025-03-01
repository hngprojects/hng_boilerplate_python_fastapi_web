import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from main import app  
from api.v1.models.job import Job  
from api.v1.models.bookmark import Bookmark 
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.bookmark import bookmark_service
from api.db.database import get_db 

@pytest.fixture
def mock_user():
    return MagicMock(id='test_user_id')  

@pytest.fixture
def mock_job():
    return Job(id='test_job_id')  

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.fixture
def override_get_db(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture
def client(mock_user, override_get_db):
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_create_bookmark_success(mock_db, mock_user, mock_job, client):
    # Set up mock_db to return mock_job
    mock_db.query.return_value.filter.return_value.first.return_value = mock_job
    
    # Patch the bookmark_service.create method
    with patch('api.v1.services.bookmark.bookmark_service.create') as mock_create:
        mock_create.return_value = Bookmark(id='new_bookmark_id')
        
        response = client.post(
            f"/api/v1/jobs/bookmark/{mock_job.id}",
            json={"job_id": mock_job.id}
        )
        
        assert response.status_code == 200
        assert response.json() == {
            "status": "success",
            "message": "Job saved successfully",
            "status_code": 200,
            "data": {}
        }
        
        # Verify create was called with correct parameters
        mock_create.assert_called_once_with(mock_db, mock_job.id, mock_user.id)

def test_create_bookmark_already_exists(mock_db, mock_user, mock_job, client):
    # Set up mock_db to return mock_job
    mock_db.query.return_value.filter.return_value.first.return_value = mock_job
    
    # Patch the bookmark_service.create method to raise an exception
    with patch('api.v1.services.bookmark.bookmark_service.create') as mock_create:
        mock_create.side_effect = HTTPException(
            status_code=400,
            detail="Job already saved"
        )
        
        response = client.post(
            f"/api/v1/jobs/bookmark/{mock_job.id}",
            json={"job_id": mock_job.id}
        )
        
        assert response.status_code == 200
        assert response.json() == {
            "status": "failure",
            "message": "Job already saved",
            "status_code": 400,
            "data": {}
        }
        
        # Verify create was called with correct parameters
        mock_create.assert_called_once_with(mock_db, mock_job.id, mock_user.id)

def test_create_bookmark_job_not_exist(mock_db, mock_user, client):
    # Mock the database query to return None for a non-existent job
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    non_existent_job_id = 'non_existent_job_id'
    
    # No need to patch bookmark_service.create since it shouldn't be called
    response = client.post(
        f"/api/v1/jobs/bookmark/{non_existent_job_id}",
        json={"job_id": non_existent_job_id}
    )
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "failure",
        "message": "Job not listed",
        "status_code": 400,
        "data": {}
    }