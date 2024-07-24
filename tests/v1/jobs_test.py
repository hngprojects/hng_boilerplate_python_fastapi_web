import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import sys, os
# Mock environment variables
os.environ['MAIL_USERNAME'] = 'test@example.com'
os.environ['MAIL_PASSWORD'] = 'password'
os.environ['MAIL_FROM'] = 'no-reply@example.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_SERVER'] = 'smtp.example.com'
os.environ['SECRET_KEY'] = 'your_secret_key'
os.environ['DB_URL'] = 'sqlite:///./test.db'

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.job import Job
from api.v1.services.user import UserService
from datetime import datetime, timedelta
import jwt
import uuid

client = TestClient(app)
user_service = UserService()

# Mock environment variables
os.environ['SECRET_KEY'] = 'your_secret_key'

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"

def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@pytest.fixture(scope="module")
def db():
    db_session = next(get_db())
    yield db_session
    db_session.close()

def create_test_admin_user(db: Session):
    hashed_password = user_service.hash_password(password="adminpassword")
    admin_user = User(
        id=uuid.uuid4(),
        username="adminuser",
        email="adminuser@example.com",
        password=hashed_password,
        is_active=True,
        is_admin=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user

def create_test_user(db: Session):
    hashed_password = user_service.hash_password(password="userpassword")
    test_user = User(
        id=uuid.uuid4(),
        username="testuser",
        email="testuser@example.com",
        password=hashed_password,
        is_active=True,
        is_admin=False
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    return test_user

@pytest.fixture(scope="module", autouse=True)
def setup_users(db: Session):
    create_test_admin_user(db)
    create_test_user(db)

def get_token(username: str, password: str):
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token

def test_create_job(db: Session):
    token = get_token("adminuser", "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    
    job_data = {
        "title": "New Job",
        "description": "New Description",
        "location": "New Location",
        "salary": 1500.0,
        "job_type": "Part-time",
        "company_name": "New Company",
        "tags": ["Engineering", "Remote"]
    }
    
    response = client.post("/api/v1/jobs/", headers=headers, json=job_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["title"] == "New Job"
    assert response_data["description"] == "New Description"
    assert response_data["location"] == "New Location"
    assert response_data["salary"] == 1500.0
    assert response_data["job_type"] == "Part-time"
    assert response_data["company_name"] == "New Company"
    assert response_data["tags"] == ["Engineering", "Remote"]

def test_get_job(db: Session):
    token = get_token("adminuser", "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a job to retrieve
    job = Job(
        user_id="admin_user_id",
        title="Job to Retrieve",
        description="Job Description",
        location="Job Location",
        salary=2000.0,
        job_type="Full-time",
        company_name="Company Name",
        tags=["Full-time", "On-site"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    response = client.get(f"/api/v1/jobs/{job.id}", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == "Job to Retrieve"
    assert response_data["description"] == "Job Description"
    assert response_data["location"] == "Job Location"
    assert response_data["salary"] == 2000.0
    assert response_data["job_type"] == "Full-time"
    assert response_data["company_name"] == "Company Name"
    assert response_data["tags"] == ["Full-time", "On-site"]

def test_create_job_unauthorized(db: Session):
    token = get_token("testuser", "userpassword")
    headers = {"Authorization": f"Bearer {token}"}
    
    job_data = {
        "title": "Unauthorized Job",
        "description": "This should not be created.",
        "location": "Unauthorized Location",
        "salary": 2500.0,
        "job_type": "Part-time",
        "company_name": "Unauthorized Company",
        "tags": ["Unauthorized"]
    }
    
    response = client.post("/api/v1/jobs/", headers=headers, json=job_data)
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have permission to perform this action."}
