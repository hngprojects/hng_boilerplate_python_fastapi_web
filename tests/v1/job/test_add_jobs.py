# Dependencies:
# pip install pytest-mock
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from api.db.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from api.v1.schemas.jobs import JobCreateResponseSchema
from api.v1.services.user import oauth2_scheme


def mock_deps():
    return MagicMock(id="user_id")

def mock_db():
    return MagicMock(spec=Session)

def mock_oauth():
    return 'access_token'

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

class TestCodeUnderTest:
    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = mock_deps
        app.dependency_overrides[get_db] = mock_db

        
    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}


    # Successfully adding a job to the database
    def test_add_jobs_success(self, client):
        test_job = {"title": "Designer",
                    "description": "A graphic artist",
                    "company_name": "HNG"}
                
        with patch('api.v1.services.jobs.job_service.create') as mock_job:
            mock_job.return_value = MagicMock(spec=JobCreateResponseSchema,
            id='user_id',
            created_at=datetime.now())

            with patch('api.v1.schemas.jobs.JobCreateResponseSchema.model_validate') as sc:
                sc.return_value = test_job
                response = client.post("/api/v1/jobs", json=test_job)

                assert response.status_code == 201
                assert response.json()['message'] == "Job listing created successfully"

                assert response.json()['data']['title'] == test_job['title']
                assert response.json()['success'] == True

    # Handling empty title field and raising appropriate exception
    def test_add_jobs_empty_title(self, client):
        test_job = {"title": "",
                    "description": "A graphic artist",
                    "company_name": "HNG"}
                

        response = client.post("/api/v1/jobs", json=test_job)
        assert response.status_code == 400
        assert response.json()['message'] == 'Invalid request data'
        # assert response.json()['success'] == False

    
    # Handling absent description field and raising appropriate exception
    def test_add_jobs_absent_description(self, client):
        test_job = {"title": "Hala",
                    "company_name": "HNG"}
        
        response = client.post("/api/v1/jobs", json=test_job)
        assert response.status_code == 422

    # Handling unauthorized request
    def test_add_jobs_unauthorized(self, client):
        test_job = {"title": "Hala",
                    "description": 'Work',
                    "company_name": "HNG"}
        
        app.dependency_overrides = {}

        response = client.post("/api/v1/jobs", json=test_job)
        assert response.status_code == 401
        assert response.json()['message'] == 'Not authenticated'
        # assert response.json()['success'] == False
        
  # Handling forbidden request
    def test_add_jobs_forbidden(self, client):
        test_job = {"title": "Hala",
                    "description": 'Work',
                    "company_name": "HNG"}
        
        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = mock_db
        app.dependency_overrides[oauth2_scheme] = mock_oauth


        # from api.v1.services.user import user_service
        with patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_superadmin=False)) as cu:
            response = client.post("/api/v1/jobs", json=test_job)
        assert response.status_code == 403
        assert response.json()['message'] == 'You do not have permission to access this resource'
        # assert response.json()['success'] == False
        