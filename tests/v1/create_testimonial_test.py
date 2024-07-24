import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from main import app  # Assuming your FastAPI app is defined in a module named main
from api.v1.schemas import testimonial_schema, user
from api.v1.models.user import User
from api.v1.services.user import user_service

# Create a new database session for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency override to use test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Dependency override to use a mock current user
def override_get_current_user():
    return User(id=1, username="testuser", email="test@example.com", hashed_password="fakehashedpassword")

app.dependency_overrides[user_service.get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_create_testimonial(db):
    # Mock user to be inserted in the database
    mock_user = User(id=1, username="testuser", email="test@example.com", hashed_password="fakehashedpassword")
    db.add(mock_user)
    db.commit()
    db.refresh(mock_user)

    # Testimonial data
    testimonial_data = {
        "title": "Great service",
        "content": "The service was excellent and I highly recommend it.",
    }

    response = client.post("/testimonials", json=testimonial_data)
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == testimonial_data["title"]
    assert response_data["content"] == testimonial_data["content"]
    assert response_data["author_id"] == mock_user.id

