import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.models.comment import Comment
from api.v1.models.blog import Blog
from api.v1.schemas.reply import ReplyCreate
from uuid_extensions import uuid7

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

def create_test_user(db):
    test_user = User(id=uuid7(), name="Test User")
    db.add(test_user)
    db.commit()
    return test_user

def create_test_blog(db, user_id):
    test_blog = Blog(id=uuid7(), author_id=user_id, title="Test Blog", content="Test Content")
    db.add(test_blog)
    db.commit()
    return test_blog

def create_test_comment(db, user_id, blog_id):
    test_comment = Comment(id=uuid7(), user_id=user_id, blog_id=blog_id, content="Test Comment")
    db.add(test_comment)
    db.commit()
    return test_comment

def test_reply_to_a_comment(test_db):
    # Create a test user, blog, and comment
    user = create_test_user(test_db)
    blog = create_test_blog(test_db, user_id=user.id)
    comment = create_test_comment(test_db, user_id=user.id, blog_id=blog.id)

    # Prepare the reply data
    reply_data = {
        "content": "This is a test reply"
    }

    # Send the POST request to the endpoint
    response = client.post(
        f"/comments/{comment.id}/reply",
        json=reply_data,
        # token not included yet
        headers={"Authorization": ""}
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Reply added successfully"
    assert response.json()["data"]["content"] == "This is a test reply"
    assert response.json()["data"]["comment_id"] == comment.id
    assert response.json()["data"]["user_id"] == user.id