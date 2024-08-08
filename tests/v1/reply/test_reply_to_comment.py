import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.models.comment import Comment
from api.v1.schemas.reply import ReplyCreate

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Mock current user
def override_get_current_user():
    return User(id="test_user_id", name="Test User")

app.dependency_overrides[user_service.get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

def test_reply_to_a_comment(test_db):
    # Create a comment in the database that we can reply to (replace with actual comment creation logic)
    comment_id = "test_comment_id"
    # You might need to add code to insert a test comment here
    
    # Prepare the reply data
    reply_data = {
        "content": "This is a test reply"
    }

    # Send the POST request to the endpoint
    response = client.post(
        f"/comments/{comment_id}/reply",
        json=reply_data,
        headers={"Authorization": "Bearer test_token"}  # Use your authentication method
    )

    assert response.status_code == 201
    assert response.json() == {
        "status_code": 201,
        "message": "Reply added successfully",
        "data": {
            "id": "expected_reply_id",  # Replace with the actual logic to verify the reply ID
            "content": "This is a test reply",
            "user_id": "test_user_id",
            "comment_id": "test_comment_id"
        }
    }
