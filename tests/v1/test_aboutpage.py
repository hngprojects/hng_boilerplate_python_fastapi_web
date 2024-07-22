from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from fastapi.testclient import TestClient
from main import app
from api.v1.models.base import Base
from api.v1.models.user import User
from api.db.database import get_db
from api.v1.models.about_page import AboutPage
from api.v1.schemas.aboutpage_schema import AboutPageUpdate
from api.utils.auth import create_access_token
from api.utils.dependencies import get_current_admin
import pytest

# Setup test database
SQLALCHEMY_DATABASE_URL = config('DB_URL')
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Override get_db dependency for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Add an initial admin user and AboutPage entry
    admin_user = User(username="admin_user", email="admin@example.com", password="hashed_password", is_admin=True)
    db.add(admin_user)

    about_page = AboutPage(title="Old Title", introduction="Old Introduction", custom_sections={})
    db.add(about_page)
    db.commit()

    yield db
    # Clean up
    db.close()
    Base.metadata.drop_all(bind=engine)


# Your test cases
def test_update_about_page_success(setup_database):
    db = setup_database
    token = create_access_token(data={"username": "admin_user"}) 

    new_data = AboutPageUpdate(
        title="New Title",
        introduction="New Introduction",
        custom_sections={
            "stats": {
                "years_in_business": 20,
                "customers": 100000,
                "monthly_blog_readers": 20000,
                "social_followers": 150000
            },
            "services": {
                "title": "Our Best Services",
                "description": "We provide the best services."
            }
        }
    )

    response = client.put(
        "/api/v1/content/about",
        json=new_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    assert response.json() == {
		'message': 'About page updated successfully',
		'status_code': 200
	}

def test_update_about_page_not_found(setup_database):
    db = setup_database
    token = create_access_token(data={"username": "admin_user"}) 
    # Clear existing AboutPage entry
    db.query(AboutPage).delete()
    db.commit()

    new_data = AboutPageUpdate(
        title="Another Title",
        introduction="Another Introduction",
        custom_sections={}
    )

    response = client.put(
        "/api/v1/content/about",
        json=new_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'About page content not found'}

def test_update_about_page_unauthorized(setup_database):
    db = setup_database

    new_data = AboutPageUpdate(
        title="Unauthorized Title",
        introduction="Unauthorized Introduction",
        custom_sections={}
    )

    response = client.put(
        "/api/v1/content/about",
        json=new_data.model_dump()
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
